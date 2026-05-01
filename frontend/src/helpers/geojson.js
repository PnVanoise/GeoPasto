export function normalizeGeoData(payload) {
  if (!payload) return null;
  if (payload.type === "FeatureCollection" && Array.isArray(payload.features)) {
    return payload;
  }
  if (payload.type === "Feature") {
    return { type: "FeatureCollection", features: [payload] };
  }
  if (Array.isArray(payload)) {
    return { type: "FeatureCollection", features: payload };
  }
  if (payload.geometry) {
    return {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          geometry: payload.geometry,
          properties: payload.properties || {},
        },
      ],
    };
  }
  return null;
}

export function wrapFeature(geometry, properties = {}) {
  return { type: "Feature", geometry, properties };
}

export function wrapFeatureCollection(featuresOrFeature) {
  if (Array.isArray(featuresOrFeature)) {
    return { type: "FeatureCollection", features: featuresOrFeature };
  }
  return { type: "FeatureCollection", features: [featuresOrFeature] };
}
