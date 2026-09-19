# Dashboard — Radiografía del Puntaje Global

App Next.js (App Router + TypeScript) que presenta las 9 etapas del análisis de
Saber Pro Medicina. Es un port fiel del prototipo HTML/CSS/JS de referencia a
componentes React reales.

## Desarrollo

```bash
npm install
npm run dev
```

Abre `http://localhost:3000`.

## Build de producción

```bash
npm run build
npm start
```

## Independencia del resto del repo

Esta app **no lee ni escribe nada de `docs/` en runtime**. Todos los datos
numéricos de las 9 etapas están hardcodeados y tipados en
`src/data/etapas.ts`, y las 3 imágenes de evidencia (SHAP summary plot, UMAP
etapa 4, UMAP etapa 9) están copiadas en `public/img/`. Se puede mover,
desplegar o construir `dashboard/` de forma completamente aislada del resto
del proyecto de análisis.
