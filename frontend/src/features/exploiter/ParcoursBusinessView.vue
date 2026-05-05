<template>
  <div class="parcours-business-view">
    <div v-if="summary.overlapDays > 0" class="summary-grid">
      <article v-if="summary.overlapDays > 0" class="summary-card summary-card--warning">
        <p class="summary-label">Jours en chevauchement</p>
        <p class="summary-value">{{ summary.overlapDays }}</p>
      </article>
    </div>

    <section class="cards-list-card">
      <header class="section-head">
        <h5>Jours et animaux par quartier
          <p>(Jours/animaux/UGB = jours x effectif x coefficient UGB du troupeau.)</p>
        </h5>
      </header>

      <div v-if="!quartierIndicators.length" class="empty-state">
        Aucune donnee quartier disponible.
      </div>

      <div v-else class="quartier-metrics-list">
        <article
          v-for="metric in quartierIndicators"
          :key="metric.key"
          class="quartier-metric-card"
        >
          <p class="quartier-metric-line">
            <strong>{{ metric.codeLabel }}</strong>
            <span> - {{ metric.nameLabel }}</span>
            <span> - <strong>{{ metric.days }}</strong> jours</span>
            <span> - <strong>{{ metric.animalUgbDaysLabel }}</strong> j/UGB</span>
          </p>
          <p v-if="metric.hasAllHerdsSegment" class="quartier-metric-note-inline">
            (inclut "Tous les troupeaux")
          </p>
        </article>
      </div>
    </section>

    <section class="timeline-card">
      <header class="section-head">
        <h5>Frise de paturage par quartier</h5>
        <p>
          Fenetre :
          <strong>{{ formatDisplayDate(timelineBounds.start) }}</strong>
          a
          <strong>{{ formatDisplayDate(timelineBounds.end) }}</strong>
        </p>
      </header>

      <div v-if="props.isLoading" class="empty-state">
        Chargement des parcours...
      </div>

      <div v-else-if="!normalizedParcours.length" class="empty-state">
        Aucun parcours enregistre pour cette situation.
      </div>

      <div v-else class="timeline-body">
        <div v-for="(row, rowIndex) in timelineRows" :key="row.key" class="timeline-row">
          <div class="timeline-row-label">{{ row.label }}</div>
          <div class="timeline-track" :style="{ minHeight: `${row.trackMinHeight}px` }">
            <div
              v-if="todayMarker.isVisible"
              class="timeline-today-marker"
              :style="{ left: `${todayMarker.leftPct}%` }"
              title="Date actuelle"
              aria-label="Date actuelle"
            >
              <span v-if="rowIndex === 0" class="today-marker-label">Auj.</span>
            </div>
            <button
              v-for="segment in row.segments"
              :key="segment.id"
              type="button"
              class="timeline-segment"
              :class="{ 'is-selected': selectedParcoursId === segment.id }"
              :style="segment.style"
              :title="segment.tooltip"
              @click="selectedParcoursId = segment.id"
            >
              <span class="segment-label">{{ segment.shortLabel }}</span>
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";

const props = defineProps({
  parcoursItems: {
    type: Array,
    default: () => [],
  },
  cheptelsItems: {
    type: Array,
    default: () => [],
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
  quartiersGeoData: {
    type: Object,
    default: null,
  },
  situationStartDate: {
    type: String,
    default: "",
  },
  situationEndDate: {
    type: String,
    default: "",
  },
});

const selectedParcoursId = ref(null);

const toDate = (input) => {
  if (!input) return null;

  if (typeof input === "string") {
    const dmyMatch = input.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
    if (dmyMatch) {
      const value = new Date(Number(dmyMatch[3]), Number(dmyMatch[2]) - 1, Number(dmyMatch[1]));
      if (!Number.isNaN(value.getTime())) {
        value.setHours(0, 0, 0, 0);
        return value;
      }
    }
  }

  const value = input instanceof Date ? input : new Date(input);
  if (Number.isNaN(value.getTime())) return null;
  value.setHours(0, 0, 0, 0);
  return value;
};

const toSafeNumber = (value) => {
  if (value == null || value === "") return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
};

const dateDiffDays = (a, b) => {
  if (!a || !b) return 0;
  const ms = 24 * 60 * 60 * 1000;
  return Math.round((b.getTime() - a.getTime()) / ms);
};

const buildQuartierMetaById = (geoData) => {
  const map = new Map();
  const features = geoData?.features || [];
  features.forEach((feature) => {
    const propsData = feature?.properties || {};
    const rawId = propsData.id_quartier ?? feature?.id ?? propsData.id;
    const code = propsData.code_quartier || "-";
    const name = propsData.nom_quartier || propsData.code_quartier || `Quartier ${rawId ?? "?"}`;
    if (rawId != null) {
      map.set(String(rawId), { code, name });
    }
  });
  return map;
};

const quartierMetaById = computed(() => buildQuartierMetaById(props.quartiersGeoData));

const cheptelAnimalsById = computed(() => {
  const map = new Map();
  (props.cheptelsItems || []).forEach((cheptel) => {
    const id = cheptel?.id_cheptel ?? cheptel?.id;
    if (id == null) return;
    const count = toSafeNumber(cheptel?.nombre_animaux);
    if (count == null) return;
    map.set(String(id), count);
  });
  return map;
});

const cheptelUgbCoefById = computed(() => {
  const map = new Map();
  (props.cheptelsItems || []).forEach((cheptel) => {
    const id = cheptel?.id_cheptel ?? cheptel?.id;
    if (id == null) return;

    const coef =
      toSafeNumber(cheptel?.type_cheptel_detail?.coefficient_UGB)
      ?? toSafeNumber(cheptel?.coefficient_UGB)
      ?? 0;

    map.set(String(id), coef);
  });
  return map;
});

const allCheptelsStats = computed(() => {
  return (props.cheptelsItems || []).reduce((acc, cheptel) => {
    const animaux = toSafeNumber(cheptel?.nombre_animaux) ?? 0;
    const coef =
      toSafeNumber(cheptel?.type_cheptel_detail?.coefficient_UGB)
      ?? toSafeNumber(cheptel?.coefficient_UGB)
      ?? 0;

    acc.totalAnimals += animaux;
    acc.totalWeighted += animaux * coef;
    return acc;
  }, { totalAnimals: 0, totalWeighted: 0 });
});

const normalizeParcours = (item, idx) => {
  if (!item) return null;

  const id = item.id_exploiter ?? item.id ?? `parcours_${idx + 1}`;
  const quartierRawId = item.quartier ?? item.quartier_id ?? item.id_quartier ?? item?.properties?.quartier;
  const startDate = toDate(item.date_debut);
  const endDate = toDate(item.date_fin) || startDate;

  if (!startDate || !endDate) return null;

  const quartierMeta = quartierRawId != null ? quartierMetaById.value.get(String(quartierRawId)) : null;
  const quartierNom = item.quartier_nom
    || item.nom_quartier
    || quartierMeta?.name
    || `Quartier ${quartierRawId ?? "-"}`;
  const quartierCode = item.code_quartier
    || quartierMeta?.code
    || "-";

  const duration = Math.max(1, dateDiffDays(startDate, endDate) + 1);
  const cheptelLabel = item.cheptel_nom
    || (item.cheptel == null ? "Tous les troupeaux" : null)
    || item?.cheptel_detail?.nom
    || item?.cheptel_detail?.description
    || null;

  const cheptelId = item.cheptel != null ? String(item.cheptel) : null;

  const parcoursNombreAnimaux = toSafeNumber(item?.nombre_animaux);

  const cheptelAnimals =
    parcoursNombreAnimaux
    ?? toSafeNumber(item.cheptel_nombre_animaux)
    ?? toSafeNumber(item?.cheptel_detail?.nombre_animaux)
    ?? (cheptelId != null ? cheptelAnimalsById.value.get(cheptelId) ?? null : null)
    ?? null;

  const cheptelUgbCoef =
    toSafeNumber(item?.type_cheptel_detail?.coefficient_UGB)
    ?? toSafeNumber(item?.cheptel_type_coefficient_UGB)
    ?? (cheptelId != null ? cheptelUgbCoefById.value.get(cheptelId) ?? 0 : 0);

  const weightedAverageCoef =
    allCheptelsStats.value.totalAnimals > 0
      ? (allCheptelsStats.value.totalWeighted / allCheptelsStats.value.totalAnimals)
      : 0;

  const allHerdsWeight =
    parcoursNombreAnimaux != null
      ? parcoursNombreAnimaux * weightedAverageCoef
      : allCheptelsStats.value.totalWeighted;

  return {
    id: String(id),
    quartierId: quartierRawId != null ? String(quartierRawId) : null,
    quartierNom,
    quartierCode,
    cheptelId,
    cheptelAnimals,
    parcoursNombreAnimaux,
    cheptelUgbCoef,
    isAllHerds: item.cheptel == null || item.tous_troupeaux === true,
    allHerdsWeight,
    startDate,
    endDate,
    durationDays: duration,
    commentaire: item.commentaire || "",
    cheptelLabel,
  };
};

const normalizedParcours = computed(() => {
  return (props.parcoursItems || [])
    .map((item, idx) => normalizeParcours(item, idx))
    .filter(Boolean)
    .sort((a, b) => a.startDate.getTime() - b.startDate.getTime());
});

watch(
  normalizedParcours,
  (items) => {
    if (!items.length) {
      selectedParcoursId.value = null;
      return;
    }

    const alreadySelected = items.some((item) => item.id === selectedParcoursId.value);
    if (!alreadySelected) {
      selectedParcoursId.value = items[0].id;
    }
  },
  { immediate: true }
);

const timelineBounds = computed(() => {
  const dates = normalizedParcours.value.flatMap((item) => [item.startDate, item.endDate]);

  const fallbackStart = toDate(props.situationStartDate);
  const fallbackEnd = toDate(props.situationEndDate);

  const minDate = dates.length ? new Date(Math.min(...dates.map((d) => d.getTime()))) : fallbackStart;
  const maxDate = dates.length ? new Date(Math.max(...dates.map((d) => d.getTime()))) : fallbackEnd;

  const start = minDate || new Date();
  const end = maxDate || start;

  if (start.getTime() > end.getTime()) {
    return { start: end, end: start };
  }

  return { start, end };
});

const timelineSpanDays = computed(() => {
  return Math.max(1, dateDiffDays(timelineBounds.value.start, timelineBounds.value.end) + 1);
});

const todayMarker = computed(() => {
  const today = toDate(new Date());
  if (!today) return { isVisible: false, leftPct: 0 };

  const bounds = timelineBounds.value;
  if (!bounds?.start || !bounds?.end) return { isVisible: false, leftPct: 0 };

  const todayTs = today.getTime();
  const startTs = bounds.start.getTime();
  const endTs = bounds.end.getTime();

  if (todayTs < startTs || todayTs > endTs) {
    return { isVisible: false, leftPct: 0 };
  }

  const offsetDays = Math.max(0, dateDiffDays(bounds.start, today));
  const leftPct = Math.max(0, Math.min(100, (offsetDays / timelineSpanDays.value) * 100));
  return { isVisible: true, leftPct };
});

const SEGMENT_HEIGHT = 22;
const TRACK_TOP_PADDING = 3;
const TRACK_BOTTOM_PADDING = 3;
const TRACK_ROW_GAP = 4;

const colorForGroup = (value) => {
  const palette = ["#0f766e", "#2563eb", "#7c3aed", "#be123c", "#b45309", "#0d9488", "#334155"];
  const str = String(value || "parcours");
  let hash = 0;
  for (let i = 0; i < str.length; i += 1) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return palette[Math.abs(hash) % palette.length];
};

const timelineRows = computed(() => {
  const grouped = new Map();

  normalizedParcours.value.forEach((item) => {
    const key = item.quartierId || item.quartierNom;
    if (!grouped.has(key)) {
      grouped.set(key, { key, label: item.quartierNom, segments: [] });
    }

    const startOffset = dateDiffDays(timelineBounds.value.start, item.startDate);
    const startPct = Math.max(0, (startOffset / timelineSpanDays.value) * 100);
    const widthPct = Math.max(2.5, (item.durationDays / timelineSpanDays.value) * 100);
    const colorKey = item.cheptelLabel || key;

    grouped.get(key).segments.push({
      id: item.id,
      shortLabel: item.cheptelLabel || `${item.durationDays} j`,
      tooltip: `${item.quartierNom} | ${formatDisplayDate(item.startDate)} - ${formatDisplayDate(item.endDate)}${item.cheptelLabel ? ` | ${item.cheptelLabel}` : ""}`,
      baseStyle: {
        left: `${Math.min(98, startPct)}%`,
        width: `${Math.min(100 - Math.min(98, startPct), widthPct)}%`,
        backgroundColor: colorForGroup(colorKey),
      },
      startDate: item.startDate,
      endDate: item.endDate,
    });
  });

  return Array.from(grouped.values())
    .map((row) => {
      const sortedSegments = row.segments
        .slice()
        .sort((a, b) => a.startDate.getTime() - b.startDate.getTime());

      // Assign overlapping segments to separate lanes to avoid label collisions.
      const laneEndTimes = [];
      const stackedSegments = sortedSegments.map((segment) => {
        const segStart = segment.startDate.getTime();
        const segEnd = segment.endDate.getTime();

        let laneIndex = laneEndTimes.findIndex((laneEnd) => segStart > laneEnd);
        if (laneIndex === -1) {
          laneIndex = laneEndTimes.length;
          laneEndTimes.push(segEnd);
        } else {
          laneEndTimes[laneIndex] = segEnd;
        }

        return {
          ...segment,
          style: {
            ...segment.baseStyle,
            top: `${TRACK_TOP_PADDING + laneIndex * (SEGMENT_HEIGHT + TRACK_ROW_GAP)}px`,
            zIndex: `${laneIndex + 1}`,
          },
        };
      });

      const laneCount = Math.max(1, laneEndTimes.length);
      const trackMinHeight =
        TRACK_TOP_PADDING
        + TRACK_BOTTOM_PADDING
        + laneCount * SEGMENT_HEIGHT
        + (laneCount - 1) * TRACK_ROW_GAP;

      return {
        ...row,
        segments: stackedSegments,
        trackMinHeight,
      };
    })
    .sort((a, b) => a.label.localeCompare(b.label));
});

const summary = computed(() => {
  // Count days where the same herd is declared on at least two different quartiers.
  const DAY_MS = 24 * 60 * 60 * 1000;
  const perHerd = new Map();

  normalizedParcours.value
    .filter((item) => item.cheptelId && item.quartierId)
    .forEach((item) => {
      if (!perHerd.has(item.cheptelId)) {
        perHerd.set(item.cheptelId, []);
      }
      perHerd.get(item.cheptelId).push(item);
    });

  let overlapDays = 0;

  perHerd.forEach((segments) => {
    const eventsByTs = new Map();

    segments.forEach((seg) => {
      const startTs = seg.startDate.getTime();
      const endExclusiveTs = seg.endDate.getTime() + DAY_MS;

      if (!eventsByTs.has(startTs)) {
        eventsByTs.set(startTs, { add: [], remove: [] });
      }
      eventsByTs.get(startTs).add.push(seg.quartierId);

      if (!eventsByTs.has(endExclusiveTs)) {
        eventsByTs.set(endExclusiveTs, { add: [], remove: [] });
      }
      eventsByTs.get(endExclusiveTs).remove.push(seg.quartierId);
    });

    const sortedTs = Array.from(eventsByTs.keys()).sort((a, b) => a - b);
    const activeQuartierCount = new Map();

    for (let i = 0; i < sortedTs.length; i += 1) {
      const ts = sortedTs[i];
      const event = eventsByTs.get(ts);

      event.remove.forEach((quartierId) => {
        const nextCount = (activeQuartierCount.get(quartierId) || 0) - 1;
        if (nextCount <= 0) activeQuartierCount.delete(quartierId);
        else activeQuartierCount.set(quartierId, nextCount);
      });

      event.add.forEach((quartierId) => {
        const nextCount = (activeQuartierCount.get(quartierId) || 0) + 1;
        activeQuartierCount.set(quartierId, nextCount);
      });

      const nextTs = sortedTs[i + 1];
      if (nextTs == null || nextTs <= ts) continue;

      if (activeQuartierCount.size >= 2) {
        overlapDays += Math.round((nextTs - ts) / DAY_MS);
      }
    }
  });

  return { overlapDays };
});

const quartierIndicators = computed(() => {
  const byQuartier = new Map();
  const DAY_MS = 24 * 60 * 60 * 1000;

  normalizedParcours.value.forEach((item) => {
    const key = item.quartierId || item.quartierNom || "-";
    if (!byQuartier.has(key)) {
      byQuartier.set(key, {
        key,
        code: item.quartierCode || "-",
        label: item.quartierNom,
        hasAllHerdsSegment: false,
        dayWeights: new Map(),
      });
    }

    const target = byQuartier.get(key);

    if (item.isAllHerds) {
      target.hasAllHerdsSegment = true;
    }

    for (
      let ts = item.startDate.getTime();
      ts <= item.endDate.getTime();
      ts += DAY_MS
    ) {
      const dayKey = String(ts);
      if (!target.dayWeights.has(dayKey)) {
        target.dayWeights.set(dayKey, { hasAllHerds: false, allHerdsWeight: 0, specificWeight: 0 });
      }

      const dayState = target.dayWeights.get(dayKey);

      if (item.isAllHerds) {
        dayState.hasAllHerds = true;
        dayState.allHerdsWeight = Math.max(dayState.allHerdsWeight || 0, item.allHerdsWeight || 0);
        continue;
      }

      if (item.cheptelId && Number.isFinite(item.cheptelAnimals)) {
        dayState.specificWeight += item.cheptelAnimals * (item.cheptelUgbCoef ?? 0);
      }
    }
  });

  return Array.from(byQuartier.values())
    .map((entry) => {
      const animalUgbDays = Array.from(entry.dayWeights.values()).reduce((sum, dayState) => {
        if (dayState.hasAllHerds) {
          return sum + (dayState.allHerdsWeight || 0);
        }
        return sum + dayState.specificWeight;
      }, 0);

      return {
        key: entry.key,
        codeLabel: entry.code,
        nameLabel: entry.label,
        days: entry.dayWeights.size,
        animalUgbDaysLabel: String(Math.round((animalUgbDays + Number.EPSILON) * 100) / 100),
        hasAllHerdsSegment: entry.hasAllHerdsSegment,
      };
    })
    .sort((a, b) => `${a.codeLabel} ${a.nameLabel}`.localeCompare(`${b.codeLabel} ${b.nameLabel}`));
});

const formatDisplayDate = (date) => {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) return "-";
  return date.toLocaleDateString("fr-FR");
};
</script>

<style scoped>
.parcours-business-view {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.45rem;
}

.summary-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  text-align: left;
  background: linear-gradient(180deg, #ffffff 0%, #f6f9fc 100%);
  border: 1px solid #d8e1ec;
  border-radius: 10px;
  padding: 0.45rem 0.55rem;
  min-height: 80px;
}

.summary-card--warning {
  border-color: #f3d8b0;
  background: linear-gradient(180deg, #fff9f0 0%, #fff3dd 100%);
}

.summary-label {
  margin: 0;
  color: #475569;
  font-size: 0.72rem;
  line-height: 1.2;
  min-height: calc(2 * 0.72rem * 1.2);
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  width: 100%;
  text-align: left;
}

.summary-value {
  margin: 0.15rem 0 0 0;
  color: #0f172a;
  font-size: 1.15rem;
  line-height: 1;
  font-weight: 700;
  width: 100%;
  text-align: left;
}

.timeline-card,
.cards-list-card {
  border: 1px solid #dbe3ee;
  border-radius: 10px;
  padding: 0.65rem;
  background: #ffffff;
}

.section-head h5 {
  margin: 0;
  color: #0f172a;
  font-size: 0.9rem;
}

.section-head p {
  margin: 0.15rem 0 0 0;
  color: #64748b;
  font-size: 0.75rem;
}

.timeline-body {
  margin-top: 0.55rem;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.timeline-row {
  display: grid;
  grid-template-columns: 150px minmax(0, 1fr);
  gap: 0.5rem;
  align-items: center;
}

.timeline-row-label {
  color: #1e293b;
  font-size: 0.76rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.timeline-track {
  position: relative;
  min-height: 30px;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  background: repeating-linear-gradient(
    90deg,
    #f8fafc 0,
    #f8fafc 16px,
    #f1f5f9 16px,
    #f1f5f9 32px
  );
}

.timeline-segment {
  position: absolute;
  top: 3px;
  height: 22px;
  border: 0;
  border-radius: 6px;
  color: #ffffff;
  font-size: 0.67rem;
  padding: 0 0.35rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.2);
  /* transition: transform 120ms ease, box-shadow 120ms ease; */
}

.timeline-today-marker {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 0;
  border-left: 2px dashed #ef4444;
  pointer-events: none;
  z-index: 50;
}

.today-marker-label {
  position: absolute;
  top: -18px;
  left: -14px;
  background: #ef4444;
  color: #ffffff;
  border-radius: 10px;
  font-size: 0.6rem;
  line-height: 1;
  padding: 2px 5px;
}

.timeline-segment:hover {
  /* transform: translateY(-1px); */
  box-shadow: 0 4px 11px rgba(15, 23, 42, 0.25);
}

.timeline-segment.is-selected {
  outline: 2px solid #0f172a;
}

.segment-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-state {
  margin-top: 0.55rem;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  padding: 0.8rem;
  color: #64748b;
  font-size: 0.78rem;
  text-align: center;
}

.quartier-metrics-list {
  margin-top: 0.55rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.45rem;
}

.quartier-metric-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.5rem 0.55rem;
  background: #f8fafc;
}

.quartier-metric-line {
  margin: 0;
  font-size: 0.75rem;
  line-height: 1.35;
  color: #334155;
}

.quartier-metric-note-inline {
  margin: 0.2rem 0 0 0;
  display: block;
  color: #92400e;
  font-size: 0.7rem;
}

@media (max-width: 760px) {
  .quartier-metrics-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1200px) {
  .summary-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .summary-card {
    min-height: 76px;
  }
}

@media (max-width: 760px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .summary-card {
    min-height: 74px;
  }

  .timeline-row {
    grid-template-columns: 1fr;
  }

  .timeline-row-label {
    white-space: normal;
  }

}
</style>
