import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import auth from "@/services/axios";
import config from "@/../config";

export function useSituationGeoData(form, { activeBottomTab } = {}) {
  // ── State ─────────────────────────────────────────────────────────────────
  const eventTypes = ref([]);
  const cheptels = ref([]);
  const parcoursItems = ref([]);
  const gardesData = ref([]);
  const quartiersGeoData = ref(null);
  const evenementsGeoData = ref(null);
  const equipementsUpGeoData = ref(null);
  const equipementsSituationGeoData = ref(null);
  const unitePastoraleGeoData = ref(null);
  const mesuresDePlanGeoData = ref(null);
  const isQuartiersMapLoading = ref(false);
  const isEvenementsMapLoading = ref(false);
  const isEquipementsUpMapLoading = ref(false);
  const isEquipementsSituationMapLoading = ref(false);
  const isUpMapLoading = ref(false);
  const isMesuresDePlanMapLoading = ref(false);
  const isParcoursLoading = ref(false);

  const isMapLoading = computed(
    () =>
      isQuartiersMapLoading.value ||
      isEvenementsMapLoading.value ||
      isEquipementsUpMapLoading.value ||
      isEquipementsSituationMapLoading.value ||
      isUpMapLoading.value ||
      isMesuresDePlanMapLoading.value
  );

  // ── Computed ──────────────────────────────────────────────────────────────
  const upGeometry = computed(() => {
    const features = unitePastoraleGeoData.value?.features;
    if (!Array.isArray(features) || !features.length) return null;
    return features[0]?.geometry ?? null;
  });

  const hasQuartiersForSituation = computed(() => {
    const features = quartiersGeoData.value?.features;
    return Array.isArray(features) && features.length > 0;
  });

  const gardesSummary = computed(() =>
    gardesData.value.map((g) => {
      const name = [g.berger_prenom, g.berger_nom].filter(Boolean).join(" ") || "—";
      const fmt = (d) => (d ? d.split("-").reverse().join("/") : "?");
      return `${name} · ${fmt(g.date_debut)} – ${g.date_fin ? fmt(g.date_fin) : "…"}`;
    })
  );

  const mapLayers = computed(() => [
    {
      id: "up_outline",
      title: "Unité pastorale",
      showInSwitcher: false,
      data: unitePastoraleGeoData.value,
      style: {
        strokeColor: "#b23a2a",
        strokeWidth: 5,
        fillOpacity: 0,
        lineDash: [10, 7],
        zIndex: 12,
      },
      popup: { typeLabel: "UP", attribute: "nom_up", idAttribute: "id_unite_pastorale", route: "" },
    },
    {
      id: "quartier",
      title: "Quartiers",
      data: quartiersGeoData.value,
      style: { strokeColor: "#1f6f8b", strokeWidth: 3, fillOpacity: 0.16, zIndex: 10 },
      popup: {
        typeLabel: "Quartier",
        attribute: "nom_quartier",
        idAttribute: "id_quartier",
        route: "/QuartierPasto/edit",
      },
    },
    {
      id: "evenement",
      title: "Événements",
      data: evenementsGeoData.value,
      style: {
        strokeColor: "#dc2626",
        strokeWidth: 2,
        fillOpacity: 0.14,
        pointRadius: 6.5,
        pointShape: "triangle",
        pointStrokeColor: "#ffffff",
        pointStrokeWidth: 1,
        zIndex: 15,
      },
      popup: {
        typeLabel: "Événement",
        attribute: "description",
        idAttribute: "event_id",
        route: "/Evenement/edit",
        contentType: "eventCompact",
      },
    },
    {
      id: "equipement_up",
      title: "Équip. alpage",
      data: equipementsUpGeoData.value,
      style: {
        strokeColor: "#16a34a",
        strokeWidth: 2,
        fillOpacity: 0.2,
        pointRadius: 5.8,
        pointShape: "square",
        pointStrokeColor: "#ffffff",
        pointStrokeWidth: 1,
        zIndex: 14,
      },
      popup: {
        typeLabel: "Équipement alpage",
        attribute: "description",
        idAttribute: "id_equipement_alpage",
        route: "",
      },
    },
    {
      id: "equipement_situation",
      title: "Équip. exploitant",
      data: equipementsSituationGeoData.value,
      style: {
        strokeColor: "#2563eb",
        strokeWidth: 2,
        fillOpacity: 0.2,
        pointRadius: 5.8,
        pointShape: "square",
        pointStrokeColor: "#ffffff",
        pointStrokeWidth: 1,
        zIndex: 14,
      },
      popup: {
        typeLabel: "Équipement exploitant",
        attribute: "description",
        idAttribute: "id_equipement_exploitant",
        route: "",
      },
    },
    {
      id: "mesure_plan",
      title: "Mesures de plan",
      data: mesuresDePlanGeoData.value,
      style: {
        strokeColor: "#7c3aed",
        strokeWidth: 2,
        fillOpacity: 0.18,
        pointRadius: 5.5,
        pointStrokeColor: "#ffffff",
        pointStrokeWidth: 1,
        zIndex: 13,
      },
      popup: {
        typeLabel: "Mesure",
        attribute: "popup_label",
        idAttribute: "id_mesure_plan",
        route: "",
      },
    },
  ]);

  const mapHasData = computed(() =>
    mapLayers.value.some((layer) => {
      const features = layer?.data?.features;
      return Array.isArray(features) && features.length > 0;
    })
  );

  // ── Normalize helpers ─────────────────────────────────────────────────────
  const toFeatureCollection = (payload, idKey) => {
    if (!payload) return null;
    if (payload.type === "FeatureCollection" && Array.isArray(payload.features)) return payload;
    if (payload.type === "Feature") return { type: "FeatureCollection", features: [payload] };
    if (Array.isArray(payload)) {
      const features = payload
        .map((item) => {
          if (!item) return null;
          if (item.type === "Feature") return item;
          if (!item.geometry) return null;
          return {
            type: "Feature",
            id: item[idKey] ?? item.id ?? item.properties?.[idKey],
            geometry: item.geometry,
            properties: item.properties ?? item,
          };
        })
        .filter(Boolean);
      return { type: "FeatureCollection", features };
    }
    return null;
  };

  const normalizeUpGeoData = (payload) => {
    const base = toFeatureCollection(payload, "id_unite_pastorale");
    if (base) return base;
    if (payload?.geometry) {
      return {
        type: "FeatureCollection",
        features: [
          {
            type: "Feature",
            id: payload.id_unite_pastorale ?? payload.id,
            geometry: payload.geometry,
            properties: payload.properties ?? payload,
          },
        ],
      };
    }
    return null;
  };

  const normalizeParcoursItems = (payload) => {
    if (!payload) return [];
    const extractItem = (item) => {
      if (!item) return null;
      if (item.type === "Feature") {
        const p = item.properties || {};
        return { ...p, id_exploiter: p.id_exploiter ?? item.id ?? p.id };
      }
      return item;
    };
    if (payload.type === "FeatureCollection" && Array.isArray(payload.features))
      return payload.features.map(extractItem).filter(Boolean);
    if (payload.type === "Feature") return [extractItem(payload)].filter(Boolean);
    if (Array.isArray(payload)) return payload.map(extractItem).filter(Boolean);
    return [];
  };

  const geometryPriority = (type) => {
    if (type === "Polygon" || type === "MultiPolygon") return 4;
    if (type === "LineString" || type === "MultiLineString") return 3;
    if (type === "Point" || type === "MultiPoint") return 2;
    return 1;
  };

  const dedupeEventFeatures = (features) => {
    if (!Array.isArray(features)) return [];
    const chosen = new Map();
    const withoutId = [];
    features.forEach((feature) => {
      const eventId = feature?.properties?.event_id;
      if (eventId == null) {
        withoutId.push(feature);
        return;
      }
      const key = String(eventId);
      const current = chosen.get(key);
      if (
        !current ||
        geometryPriority(feature?.geometry?.type) >= geometryPriority(current?.geometry?.type)
      ) {
        chosen.set(key, feature);
      }
    });
    return [...chosen.values(), ...withoutId];
  };

  // ── Fetch functions ───────────────────────────────────────────────────────
  const fetchUnitePastoraleGeometry = async () => {
    if (!form.unite_pastorale) {
      unitePastoraleGeoData.value = null;
      return;
    }
    isUpMapLoading.value = true;
    try {
      const [upResp, geomResp] = await Promise.all([
        auth.axiosInstance.get(
          `${config.API_BASE_URL}/api/unitePastorale/${form.unite_pastorale}/`
        ),
        auth.axiosInstance.get(`${config.API_BASE_URL}/api/geometrieUP/`, {
          params: { unite_pastorale: form.unite_pastorale },
        }),
      ]);

      // Référence temporelle : date_debut de la situation, ou 1er jan de l'année
      const refDate = form.date_debut || null;

      // Chercher la géométrie valide à la date de référence
      let historicalGeometry = null;
      if (refDate) {
        const histFeatures = geomResp.data?.features ?? [];
        const match = histFeatures.find((f) => {
          const debut = f.properties?.date_debut_validite;
          const fin = f.properties?.date_fin_validite;
          return debut && debut <= refDate && (!fin || fin >= refDate);
        });
        if (match) historicalGeometry = match.geometry ?? null;
      }

      // Construire les features en remplaçant la géométrie si trouvée dans l'historique
      const upFeatures = (normalizeUpGeoData(upResp.data)?.features || [])
        .filter((f) => f?.geometry || historicalGeometry)
        .map((f) => {
          const rawId = f?.id ?? f?.properties?.id_unite_pastorale ?? f?.properties?.id;
          return {
            ...f,
            id: rawId != null ? `up:${rawId}` : undefined,
            geometry: historicalGeometry ?? f.geometry,
            properties: {
              ...(f?.properties || {}),
              id_unite_pastorale: rawId ?? f?.properties?.id_unite_pastorale,
            },
          };
        });

      unitePastoraleGeoData.value = { type: "FeatureCollection", features: upFeatures };
    } catch {
      unitePastoraleGeoData.value = null;
    } finally {
      isUpMapLoading.value = false;
    }
  };

  const fetchQuartiersForSituation = async () => {
    if (!form.id_situation) {
      quartiersGeoData.value = null;
      return;
    }
    isQuartiersMapLoading.value = true;
    try {
      const { data } = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/quartierPasto/?id_situation=${form.id_situation}`
      );
      const features = (toFeatureCollection(data, "id_quartier")?.features || []).map((f) => {
        const rawId = f?.id ?? f?.properties?.id_quartier ?? f?.properties?.id;
        return {
          ...f,
          id: rawId != null ? `quartier:${rawId}` : undefined,
          properties: {
            ...(f?.properties || {}),
            id_quartier: rawId ?? f?.properties?.id_quartier,
          },
        };
      });
      quartiersGeoData.value = { type: "FeatureCollection", features };
    } catch {
      quartiersGeoData.value = null;
    } finally {
      isQuartiersMapLoading.value = false;
    }
  };

  const fetchEvenementsForUp = async () => {
    if (!form.id_situation) {
      evenementsGeoData.value = null;
      return;
    }
    isEvenementsMapLoading.value = true;
    try {
      const { data } = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/evenement/?situation=${form.id_situation}`
      );
      const eventTypeById = new Map(
        (eventTypes.value || []).map((t) => [String(t?.id_type_evenement), t?.description])
      );
      const withMetadata = (toFeatureCollection(data, "id_evenement")?.features || [])
        .filter((f) => f?.geometry)
        .map((f) => {
          const rawId = f?.id ?? f?.properties?.id_evenement ?? f?.properties?.id;
          const rawType = f?.properties?.type_evenement;
          const typeLabel =
            rawType != null
              ? eventTypeById.get(String(rawType)) ||
                f?.properties?.type_evenement_label ||
                f?.properties?.type_evenement_detail?.description ||
                `Type ${rawType}`
              : null;
          return {
            ...f,
            id: rawId != null ? `evenement:${rawId}` : undefined,
            properties: {
              ...(f?.properties || {}),
              event_id: rawId,
              type_evenement_label: typeLabel,
              is_representative_marker: false,
            },
          };
        });
      evenementsGeoData.value = {
        type: "FeatureCollection",
        features: dedupeEventFeatures(withMetadata),
      };
    } catch {
      evenementsGeoData.value = null;
    } finally {
      isEvenementsMapLoading.value = false;
    }
  };

  const fetchEquipementsUpForUp = async () => {
    if (!form.unite_pastorale) {
      equipementsUpGeoData.value = null;
      return;
    }
    isEquipementsUpMapLoading.value = true;
    try {
      const { data } = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/equipementAlpage/?unite_pastorale=${form.unite_pastorale}`
      );
      const features = (toFeatureCollection(data, "id_equipement_alpage")?.features || [])
        .filter((f) => f?.geometry)
        .map((f) => {
          const rawId = f?.id ?? f?.properties?.id_equipement_alpage ?? f?.properties?.id;
          return {
            ...f,
            id: rawId != null ? `equipement_up:${rawId}` : undefined,
            properties: {
              ...(f?.properties || {}),
              id_equipement_alpage: rawId ?? f?.properties?.id_equipement_alpage,
            },
          };
        });
      equipementsUpGeoData.value = { type: "FeatureCollection", features };
    } catch {
      equipementsUpGeoData.value = null;
    } finally {
      isEquipementsUpMapLoading.value = false;
    }
  };

  const fetchEquipementsSituationForSituation = async () => {
    if (!form.id_situation) {
      equipementsSituationGeoData.value = null;
      return;
    }
    isEquipementsSituationMapLoading.value = true;
    try {
      const { data } = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/equipementExploitant/?id_situation=${form.id_situation}`
      );
      const features = (toFeatureCollection(data, "id_equipement_exploitant")?.features || [])
        .filter((f) => f?.geometry)
        .map((f) => {
          const rawId = f?.id ?? f?.properties?.id_equipement_exploitant ?? f?.properties?.id;
          return {
            ...f,
            id: rawId != null ? `equipement_situation:${rawId}` : undefined,
            properties: {
              ...(f?.properties || {}),
              id_equipement_exploitant: rawId ?? f?.properties?.id_equipement_exploitant,
            },
          };
        });
      equipementsSituationGeoData.value = { type: "FeatureCollection", features };
    } catch {
      equipementsSituationGeoData.value = null;
    } finally {
      isEquipementsSituationMapLoading.value = false;
    }
  };

  const fetchMesuresDePlanForUp = async () => {
    if (!form.unite_pastorale) {
      mesuresDePlanGeoData.value = null;
      return;
    }
    isMesuresDePlanMapLoading.value = true;
    try {
      const { data } = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/mesurePlan/?unite_pastorale=${form.unite_pastorale}`
      );
      const features = (toFeatureCollection(data, "id_mesure_plan")?.features || [])
        .filter((f) => f?.geometry)
        .map((f) => {
          const rawId = f?.id ?? f?.properties?.id_mesure_plan ?? f?.properties?.id;
          const typeMesure = f?.properties?.type_mesure_detail?.description;
          const desc = f?.properties?.description;
          const popupLabel =
            [typeMesure, desc].filter(Boolean).join(" – ") || desc || `Mesure ${rawId}`;
          return {
            ...f,
            id: rawId != null ? `mesure_plan:${rawId}` : undefined,
            properties: {
              ...(f?.properties || {}),
              id_mesure_plan: rawId ?? f?.properties?.id_mesure_plan,
              popup_label: popupLabel,
            },
          };
        });
      mesuresDePlanGeoData.value = { type: "FeatureCollection", features };
    } catch {
      mesuresDePlanGeoData.value = null;
    } finally {
      isMesuresDePlanMapLoading.value = false;
    }
  };

  const fetchParcoursForSituation = async () => {
    if (!form.id_situation) {
      parcoursItems.value = [];
      return;
    }
    isParcoursLoading.value = true;
    try {
      const { data } = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/exploiter/?id_situation=${form.id_situation}`
      );
      parcoursItems.value = normalizeParcoursItems(data);
    } catch {
      parcoursItems.value = [];
    } finally {
      isParcoursLoading.value = false;
    }
  };

  const fetchCheptels = () => {
    if (!form.id_situation) return;
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/cheptel?id_situation=${form.id_situation}`)
      .then(({ data }) => {
        cheptels.value = data;
      })
      .catch(() => {});
  };

  const fetchGardesForSituation = async () => {
    if (!form.id_situation) {
      gardesData.value = [];
      return;
    }
    try {
      const { data } = await auth.axiosInstance.get(
        `${config.API_BASE_URL}/api/gardeSituation/?id_situation=${form.id_situation}`
      );
      gardesData.value = Array.isArray(data) ? data : [];
    } catch {
      gardesData.value = [];
    }
  };

  // ── Utilitaire exposé ─────────────────────────────────────────────────────
  const upGeometryAsPolygon = (geometry) => {
    if (!geometry) return null;
    if (geometry.type === "Polygon") return geometry;
    if (geometry.type === "MultiPolygon" && geometry.coordinates?.length)
      return { type: "Polygon", coordinates: geometry.coordinates[0] };
    return null;
  };

  // ── Listener événements customs ───────────────────────────────────────────
  const onGeoDataChanged = ({ detail } = {}) => {
    const m = detail?.modelName;
    if (m === "cheptel" && form.id_situation) fetchCheptels();
    if (m === "exploiter" && form.id_situation) fetchParcoursForSituation();
    if (m === "quartierpasto" && form.id_situation) fetchQuartiersForSituation();
    if (m === "evenement" && form.id_situation) fetchEvenementsForUp();
    if (m === "equipementalpage" && form.unite_pastorale) fetchEquipementsUpForUp();
    if (m === "equipementexploitant" && form.id_situation) fetchEquipementsSituationForSituation();
    if (m === "gardesituation" && form.id_situation) fetchGardesForSituation();
    if (m === "mesuredeplan" && form.unite_pastorale) fetchMesuresDePlanForUp();
  };

  // ── Watches ───────────────────────────────────────────────────────────────
  watch(
    () => form.id_situation,
    (newId) => {
      if (newId) {
        fetchCheptels();
        fetchParcoursForSituation();
        fetchQuartiersForSituation();
        fetchEquipementsSituationForSituation();
        fetchGardesForSituation();
      } else {
        parcoursItems.value = [];
        quartiersGeoData.value = null;
        equipementsSituationGeoData.value = null;
        gardesData.value = [];
      }
    }
  );

  watch(
    () => form.unite_pastorale,
    (newUp) => {
      if (newUp) {
        fetchUnitePastoraleGeometry();
        fetchEvenementsForUp();
        fetchEquipementsUpForUp();
        fetchMesuresDePlanForUp();
      } else {
        unitePastoraleGeoData.value = null;
        evenementsGeoData.value = null;
        equipementsUpGeoData.value = null;
        mesuresDePlanGeoData.value = null;
      }
    }
  );

  watch([() => form.date_debut], () => {
    if (form.unite_pastorale) fetchUnitePastoraleGeometry();
  });

  watch(
    eventTypes,
    (types) => {
      if (form.id_situation && Array.isArray(types) && types.length) fetchEvenementsForUp();
    },
    { deep: true }
  );

  if (activeBottomTab) {
    watch(activeBottomTab, (tab) => {
      if (tab === "parcours-metier" && form.id_situation) {
        fetchCheptels();
        fetchParcoursForSituation();
      }
    });
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────
  onMounted(() => {
    auth.axiosInstance
      .get(`${config.API_BASE_URL}/api/typeEvenement/`)
      .then(({ data }) => {
        eventTypes.value = data || [];
      })
      .catch(() => {});
    window.addEventListener("geo-data-changed", onGeoDataChanged);
  });

  onBeforeUnmount(() => {
    window.removeEventListener("geo-data-changed", onGeoDataChanged);
  });

  return {
    cheptels,
    parcoursItems,
    gardesData,
    quartiersGeoData,
    evenementsGeoData,
    equipementsUpGeoData,
    equipementsSituationGeoData,
    unitePastoraleGeoData,
    isMapLoading,
    isParcoursLoading,
    mapLayers,
    mapHasData,
    upGeometry,
    upGeometryAsPolygon,
    hasQuartiersForSituation,
    gardesSummary,
    fetchCheptels,
    fetchParcoursForSituation,
    fetchQuartiersForSituation,
    fetchEquipementsSituationForSituation,
    fetchEquipementsUpForUp,
    fetchEvenementsForUp,
    fetchUnitePastoraleGeometry,
    fetchGardesForSituation,
    fetchMesuresDePlanForUp,
  };
}
