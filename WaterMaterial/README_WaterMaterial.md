# Single Layer Water Material – Unreal Engine 5.6

## Overview

`CreateSingleLayerWater.py` generates a production-ready **Single Layer Water**
material (`M_SingleLayerWater`) directly inside the UE5 editor using the Python
Editor Script Plugin.

### Why Single Layer Water?

UE5's *Single Layer Water* shading model is a lightweight, physically-based
water solution that supports:

- Volumetric light **absorption** and **scattering** (water colour & depth)
- Screen-space **refraction** of objects seen through the surface
- HDR **reflection** via the Reflection Capture system + Lumen (if enabled)
- Dual-layer animated **normal maps** for wave motion
- Full **Lumen** and **ray-tracing** compatibility

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Unreal Engine 5.6 | Tested on UE 5.6 |
| Python Editor Script Plugin | Enable in Edit → Plugins → Python Editor Script Plugin |
| Project Rendering | Works with both Deferred Shading and Forward Shading |
| Water Plugin (optional) | Epic's Water plugin is **not** required for this material |

---

## Quick Start

1. Enable the **Python Editor Script Plugin** and restart the editor.
2. Copy this folder into your project (anywhere on disk is fine).
3. In the editor, go to **File → Execute Python Script** and select
   `CreateSingleLayerWater.py`.
4. The material is created at `/Game/Materials/Water/M_SingleLayerWater`.
5. Open the material, assign a tileable normal map texture to the **NormalMap**
   parameter (any seamless blue-channel normal map works), and adjust the
   parameters below.

---

## Exposed Parameters

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `ShallowWaterColor` | Vector3 | `(0.01, 0.12, 0.22)` | Base colour of the surface |
| `ScatteringCoefficients` | Vector3 | `(0.05, 0.14, 0.28)` | Per-channel in-scattering (blue-green tint) |
| `AbsorptionCoefficients` | Vector3 | `(0.45, 0.18, 0.07)` | Per-channel absorption (deeper = darker) |
| `NormalMap` | Texture2D | *(none)* | Seamless tileable normal map (assign manually) |
| `NormalScale` | Scalar | `1.0` | Blends between flat (0) and full normal (1) |
| `WaveTiling1` | Scalar | `2.0` | UV tiling for the large wave layer |
| `WaveTiling2` | Scalar | `4.0` | UV tiling for the fine wave layer |
| `WavePanSpeed1` | Scalar | `0.02` | Pan speed of the large wave layer |
| `WavePanSpeed2` | Scalar | `0.01` | Pan speed (counter-direction) of the fine layer |
| `Roughness` | Scalar | `0.08` | Surface micro-roughness (0 = mirror) |
| `Specular` | Scalar | `0.5` | Fresnel specular intensity |
| `PhaseG` | Scalar | `0.8` | Henyey-Greenstein scattering phase (0–1) |
| `ColorScaleBehindWater` | Scalar | `1.0` | Brightness of refracted underwater objects |

---

## Material Graph Overview

```
TexCoord × WaveTiling1 → Panner(Speed1) ─┐
                                          ├─ BlendAngleCorrectedNormals ─┐
TexCoord × WaveTiling2 → Panner(Speed2) ─┘                              │
                                                               Lerp(flat, blended, NormalScale)
                                                                          │
                                                                     [Normal]

ShallowWaterColor ──────────────────────────────────────────────── [BaseColor]
Roughness ──────────────────────────────────────────────────────── [Roughness]
Specular  ──────────────────────────────────────────────────────── [Specular]
Constant(0) ────────────────────────────────────────────────────── [Metallic]

ScatteringCoefficients ─┐
AbsorptionCoefficients  ├─ SingleLayerWaterMaterialOutput
PhaseG                  │
ColorScaleBehindWater ──┘
```

---

## Tips

- **Normal map** – Use a seamless, high-frequency water normal map (e.g.,
  Quixel's `T_Water_N` or any similar asset). The dual-layer setup breaks
  obvious tiling.
- **Scattering vs Absorption** – Increase `ScatteringCoefficients` for
  murky/tropical water; increase `AbsorptionCoefficients` to make deep areas
  darker faster.
- **Performance** – Single Layer Water is significantly cheaper than the full
  Water plugin. It renders in a single deferred pass.
- **Material Instance** – Create a **Material Instance** from
  `M_SingleLayerWater` to override parameters at runtime without recompiling
  shaders.
- **Refraction quality** – Enable *r.Water.SingleLayer.Refraction 1* (default
  on) for proper screen-space refraction. Lower-end platforms can set it to 0.
