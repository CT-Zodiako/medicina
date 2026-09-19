# Etapa 9 - PCA/UMAP con el feature set honesto (sin identidad puntual de institución)

## Qué se hizo y por qué

La etapa 4 (`docs/etapa_4_pca_umap`) corrió PCA + UMAP sobre el feature set completo
original del proyecto, que incluye `INST_NOMBRE_INSTITUCION` (variable categórica de
~55 instituciones distintas) además de `ESTU_INST_DEPARTAMENTO` y
`ESTU_INST_MUNICIPIO`. Ese análisis mostró ~55-60 agrupaciones visuales pequeñas y
muy separadas entre sí en el scatter de UMAP, coincidentes casi exactamente con el
número de instituciones del dataset. La hipótesis planteada en ese momento era que
esas agrupaciones eran, en gran medida, "memorización de identidad de universidad"
(el modelo de reducción de dimensionalidad separa a los estudiantes principalmente
por a qué institución puntual pertenecen), y no estructura sustantiva sobre el
desempeño o el perfil socioeconómico.

Esta hipótesis es consistente con lo que encontraron las etapas 6 y 7 del proyecto:

- Etapa 6 (GroupKFold agrupando por `INST_NOMBRE_INSTITUCION`) mostró una caída fuerte
  y una varianza altísima entre folds al validar con instituciones nunca vistas,
  evidencia de sobreajuste a instituciones específicas.
- Etapa 7 (permutation importance vs. MDI) descompuso las 5 variables
  institucionales/de ubicación: solo `INST_ORIGEN` e `INST_CARACTER_ACADEMICO`
  resultaron señal real y transferible; `INST_NOMBRE_INSTITUCION`,
  `ESTU_INST_DEPARTAMENTO` y `ESTU_INST_MUNICIPIO` cayeron a los últimos puestos por
  importancia de permutación (memorización/sobreajuste puro).

La etapa 8 definió, a partir de esos hallazgos, el feature set "honesto" del
proyecto: todas las variables demográficas/socioeconómicas/familiares, más
`INST_ORIGEN` e `INST_CARACTER_ACADEMICO`, pero **sin** `INST_NOMBRE_INSTITUCION`,
`ESTU_INST_DEPARTAMENTO` ni `ESTU_INST_MUNICIPIO`.

Esta etapa 9 repite exactamente el pipeline de PCA/UMAP de la etapa 4 (mismo cálculo
de `EDAD`, mismo preprocesamiento, mismos hiperparámetros de PCA y UMAP, mismo estilo
de gráficos), cambiando únicamente el feature set de entrada al feature set honesto de
la etapa 8. El objetivo es verificar si, al remover la identidad puntual de
institución, los ~55 clusters desaparecen (lo esperable, si eran solo "un cluster por
universidad") o si persiste estructura real interesante.

### Feature set usado (idéntico al de etapa_8)

- **Numéricas:** `ESTU_INSE_INDIVIDUAL`, `EDAD`.
- **Categóricas:** `INST_ORIGEN`, `INST_CARACTER_ACADEMICO`, `ESTU_GENERO`,
  `ESTU_SEMESTRECURSA`, `PERIODO`, `FAMI_ESTRATOVIVIENDA`, `FAMI_EDUCACIONMADRE`,
  `FAMI_EDUCACIONPADRE`, `FAMI_CUANTOSCOMPARTEBAÑO`, `FAMI_TIENEAUTOMOVIL`,
  `FAMI_TIENECOMPUTADOR`, `FAMI_TIENECONSOLAVIDEOJUEGOS`, `FAMI_TIENEHORNOMICROOGAS`,
  `FAMI_TIENEINTERNET`, `FAMI_TIENELAVADORA`, `FAMI_TIENEMOTOCICLETA`,
  `FAMI_TIENESERVICIOTV`, `ESTU_HORASSEMANATRABAJA`, `ESTU_PAGOMATRICULABECA`,
  `ESTU_PAGOMATRICULACREDITO`, `ESTU_PAGOMATRICULAPADRES`, `ESTU_PAGOMATRICULAPROPIO`.
- **Explícitamente excluidas:** `INST_NOMBRE_INSTITUCION`, `ESTU_INST_DEPARTAMENTO`,
  `ESTU_INST_MUNICIPIO`.

## Varianza explicada por componente

| Componente | Etapa 4 (con institución) | Etapa 9 (feature set honesto) |
|---|---|---|
| PC1 | 4.30% | 8.03% |
| PC2 | 2.48% | 3.27% |
| PC3 | 2.36% | 3.00% |
| PC4 | 2.17% | 2.75% |
| PC5 | 1.94% | 2.68% |
| PC6 | 1.92% | 2.53% |
| PC7 | 1.83% | 2.25% |
| PC8 | 1.77% | 2.13% |
| PC9 | 1.72% | 2.09% |
| PC10 | 1.71% | 1.98% |
| **Acumulada (10 PCs)** | **~22.2%** | **~30.7%** |

La varianza explicada acumulada en 10 componentes sube de ~22.2% (etapa 4) a ~30.7%
(etapa 9). Esto es esperable: al quitar `INST_NOMBRE_INSTITUCION` (~55 categorías),
`ESTU_INST_DEPARTAMENTO` y `ESTU_INST_MUNICIPIO` (decenas de categorías cada una) del
one-hot encoding, el espacio de features se reduce drásticamente en dimensionalidad
dispersa (columnas dummy casi todas en cero salvo una), por lo que cada componente
principal remanente concentra proporcionalmente más varianza. En ambos casos la
varianza explicada sigue siendo baja en términos absolutos (no hay 1-2 componentes
dominantes), consistente con un dataset de features mayormente categóricas de baja
cardinalidad y sin una estructura lineal fuerte.

## Qué muestra ahora el scatter UMAP

- **Etapa 4 (`umap_scatter_puntaje.png` / `umap_scatter_caracter.png`):** el embedding
  muestra ~55-60 islas pequeñas, compactas y muy separadas entre sí, distribuidas de
  forma casi uniforme en el plano. En el coloreado por carácter académico
  (`umap_scatter_caracter.png`), cada isla es abrumadoramente de un solo color (azul o
  naranja), es decir, cada cluster corresponde a una sola categoría de carácter
  académico — y, dado que ese número coincide con el número de instituciones
  distintas, cada isla es esencialmente una institución puntual.
- **Etapa 9 (`umap_scatter_puntaje.png` / `umap_scatter_caracter.png`, esta etapa):**
  el patrón cambia de forma marcada. Ya no hay ~55 islas separadas y monocromáticas.
  En cambio se observa:
  - Un blobs central grande y denso, con sub-estructura interna difusa (varios lóbulos
    parcialmente fusionados, sin fronteras nítidas entre ellos).
  - Alrededor de 15-20 grupos periféricos pequeños y bien separados del blob central
    (posiblemente asociados a combinaciones categóricas poco frecuentes, p. ej.
    valores raros de `PERIODO`, `ESTU_SEMESTRECURSA` o combinaciones infrecuentes de
    variables familiares/socioeconómicas, no a identidad institucional).
  - En el coloreado por carácter académico, tanto el blob central como la mayoría de
    los grupos periféricos aparecen **mezclados** (azul y naranja entremezclados en
    la misma región), muy distinto del patrón monocromático de la etapa 4. Solo un par
    de los grupos periféricos pequeños son mayoritariamente de un solo color, pero ya
    no hay una correspondencia uno-a-uno entre "cluster" e "institución" o "carácter
    académico".

  Esto confirma visualmente que la segregación característica de la etapa 4 dependía
  de tener `INST_NOMBRE_INSTITUCION` (y las otras dos variables de ubicación
  institucional) como feature directo: al quitarlas, el patrón de "una isla por
  universidad" colapsa en un patrón mucho más consistente con ruido categórico y
  agrupamientos menores, no con una partición limpia por institución.

### Cuantificación de clusters (KMeans + silhouette score, k=2..15)

Se corrió KMeans sobre el embedding UMAP 2D de la etapa 9, probando k de 2 a 15 y
seleccionando el mejor por silhouette score (ver
`docs/etapa_9_pca_umap_sin_institucion/kmeans_silhouette_scores.csv` para el detalle
completo):

| k | silhouette | k | silhouette |
|---|---|---|---|
| 2 | 0.4229 | 9 | 0.4371 |
| 3 | 0.4646 | 10 | 0.4425 |
| 4 | 0.4134 | 11 | 0.4505 |
| 5 | 0.4059 | 12 | 0.4646 |
| 6 | 0.4441 | 13 | 0.4745 |
| 7 | 0.4432 | 14 | 0.4721 |
| 8 | 0.4552 | 15 | 0.4851 |

El máximo dentro del rango probado se alcanza en `k=15` (silhouette=0.4851), pero el
score sigue subiendo monótonamente hacia el borde superior del rango explorado (no
hay un pico claro e interior al rango 2-15). Esto es coherente con la lectura visual:
gran parte del silhouette alto viene de los ~15-20 grupos periféricos pequeños y bien
aislados (fáciles de separar, suben el score con cualquier k que les asigne su propio
cluster), mientras que el blob central grande no se divide en sub-clusters nítidos —
es más un continuo con lóbulos difusos que 40-55 grupos discretos. En contraste, en la
etapa 4 un k óptimo por este mismo criterio se habría acercado a las ~55-60 islas
reales (una por institución), muy por encima de lo que aquí se observa.

## Conclusión

La evidencia visual y cuantitativa apoya la hipótesis original: los ~55 clusters de
la etapa 4 eran, en su gran mayoría, **artefactos de identidad institucional puntual**
(un cluster por universidad, producto de que `INST_NOMBRE_INSTITUCION`,
`ESTU_INST_DEPARTAMENTO` y `ESTU_INST_MUNICIPIO` actuaban como identificadores
casi-únicos dentro del one-hot encoding), no estructura sustantiva sobre el
desempeño académico o el perfil del estudiante. Al remover esas tres variables y
quedarnos con el feature set honesto (demografía/socioeconomía/familia completas +
`INST_ORIGEN` + `INST_CARACTER_ACADEMICO`), el patrón de ~55 islas monocromáticas
desaparece y es reemplazado por un blob central difuso con sub-estructura débil, más
un número menor de grupos periféricos pequeños que ya no se alinean con institución ni
con carácter académico.

Sí persiste algo de estructura no trivial (el blob central no es un óvalo uniforme
perfecto, y hay grupos periféricos genuinos), pero es mucho más débil, menos numerosa
y menos nítida que la partición por institución de la etapa 4, y no ofrece evidencia
de una segunda fuente fuerte de agrupamiento comparable en magnitud a la de la
etapa 4.

En síntesis: la etapa 9 confirma, con un experimento controlado (mismo pipeline,
mismos datos, único cambio en el feature set), que el hallazgo visual de la etapa 4
era principalmente memorización de identidad institucional y no señal sustantiva. El
feature set honesto de la etapa 8 no solo es más defendible para modelado predictivo
(etapas 5-8), sino que también produce una representación de PCA/UMAP mucho más
consistente con lo esperado de datos socioeconómicos/demográficos reales: sin
partición artificial por identificador categórico de alta cardinalidad.
