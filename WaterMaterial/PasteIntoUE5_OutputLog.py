"""
SINGLE LAYER WATER MATERIAL – UE5.6
====================================
HOW TO USE
----------
1.  In UE5: Edit → Plugins → enable "Python Editor Script Plugin" → restart.
2.  Open the Output Log  (Window → Output Log).
3.  In the Output Log, change the input dropdown from "Cmd" to "Python".
4.  Copy everything below the dashed line and paste it into the Python input. Press Enter.
5.  Material is created at:  /Game/Materials/Water/M_SingleLayerWater
6.  Open it, assign a seamless normal-map texture to the "NormalMap" parameter, done.
-------------------------------------------------------------------------------------
"""

import unreal

M = unreal.MaterialEditingLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()

# ── Delete old asset if it exists ────────────────────────────────────────────
ASSET_PATH = "/Game/Materials/Water/M_SingleLayerWater"
if unreal.EditorAssetLibrary.does_asset_exist(ASSET_PATH):
    unreal.EditorAssetLibrary.delete_asset(ASSET_PATH)

# ── Create material ───────────────────────────────────────────────────────────
mat = AT.create_asset("M_SingleLayerWater", "/Game/Materials/Water",
                      unreal.Material, unreal.MaterialFactoryNew())

mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_SINGLE_LAYER_WATER)
mat.set_editor_property("blend_mode",    unreal.EBlendMode.BLEND_OPAQUE)
mat.set_editor_property("two_sided",     False)

# ── Helper lambdas ────────────────────────────────────────────────────────────
def vec(name, r, g, b, a, x, y):
    e = M.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("default_value", unreal.LinearColor(r, g, b, a))
    return e

def scl(name, val, x, y):
    e = M.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("default_value", val)
    return e

def tex(name, x, y):
    e = M.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    return e

def mul(x, y):
    return M.create_material_expression(mat, unreal.MaterialExpressionMultiply, x, y)

def pan(sx, sy, x, y):
    e = M.create_material_expression(mat, unreal.MaterialExpressionPanner, x, y)
    e.set_editor_property("const_speed_x", sx)
    e.set_editor_property("const_speed_y", sy)
    return e

def uv(tU, tV, x, y):
    e = M.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, x, y)
    e.set_editor_property("u_tiling", tU)
    e.set_editor_property("v_tiling", tV)
    return e

def lerp(x, y):
    return M.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate, x, y)

def const3(r, g, b, x, y):
    e = M.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, x, y)
    e.set_editor_property("constant", unreal.LinearColor(r, g, b, 1.0))
    return e

def const1(val, x, y):
    e = M.create_material_expression(mat, unreal.MaterialExpressionConstant, x, y)
    e.set_editor_property("r", float(val))
    return e

cx = M.connect_material_expressions    # (from, pin, to, pin)
cp = M.connect_material_property       # (from, pin, EMaterialProperty)
P  = unreal.EMaterialProperty

# ── Parameters ────────────────────────────────────────────────────────────────
p_base_color  = vec("ShallowWaterColor",       0.01, 0.12, 0.22, 1.0,  -1800, -800)
p_scatter     = vec("ScatteringCoefficients",  0.05, 0.14, 0.28, 1.0,  -1800, -580)
p_absorb      = vec("AbsorptionCoefficients",  0.45, 0.18, 0.07, 1.0,  -1800, -360)
p_roughness   = scl("Roughness",               0.08,                   -1800, -140)
p_specular    = scl("Specular",                0.50,                   -1800,   40)
p_phase_g     = scl("PhaseG",                  0.80,                   -1800,  220)
p_color_scale = scl("ColorScaleBehindWater",   1.00,                   -1800,  400)
p_normal_scl  = scl("NormalScale",             1.00,                   -1800,  580)
p_tiling1     = scl("WaveTiling1",             2.00,                   -1800,  760)
p_tiling2     = scl("WaveTiling2",             4.00,                   -1800,  940)
p_speed1      = scl("WavePanSpeed1",           0.02,                   -1800, 1120)
p_speed2      = scl("WavePanSpeed2",           0.01,                   -1800, 1300)

# ── Wave layer 1  (large scale, slow) ─────────────────────────────────────────
tc1   = uv(1.0, 1.0, -1400, -800)
mul1  = mul(              -1200, -800);  cx(tc1,  "", mul1, "A"); cx(p_tiling1, "", mul1, "B")
pan1  = pan(0.0, 0.0,     -1000, -800); cx(mul1, "", pan1, "Coordinate"); cx(p_speed1, "", pan1, "Speed")
norm1 = tex("NormalMap",   -800, -800); cx(pan1, "", norm1, "UVs")

# ── Wave layer 2  (fine scale, counter-pan) ───────────────────────────────────
tc2   = uv(1.0, 1.0, -1400, -400)
mul2  = mul(              -1200, -400);  cx(tc2,  "", mul2, "A"); cx(p_tiling2, "", mul2, "B")
pan2  = pan(0.0, 0.0,     -1000, -400); cx(mul2, "", pan2, "Coordinate"); cx(p_speed2, "", pan2, "Speed")
# Negate speed for counter-pan direction
neg   = M.create_material_expression(mat, unreal.MaterialExpressionMultiply, -1100, -280)
neg_c = const1(-1.0, -1200, -280)
cx(p_speed2, "", neg, "A"); cx(neg_c, "", neg, "B")
cx(mul2, "", pan2, "Coordinate"); cx(neg, "", pan2, "Speed")
norm2 = tex("NormalMap",   -800, -400); cx(pan2, "", norm2, "UVs")

# ── Blend normals ─────────────────────────────────────────────────────────────
BLEND_PATH = "/Engine/Functions/Engine_MaterialFunctions02/Utility/BlendAngleCorrectedNormals"
blend_fn = unreal.load_asset(BLEND_PATH)

if blend_fn:
    blend_node = M.create_material_expression(
        mat, unreal.MaterialExpressionMaterialFunctionCall, -500, -600)
    blend_node.set_editor_property("material_function", blend_fn)
    cx(norm1, "RGB", blend_node, "BaseNormal (V3)")
    cx(norm2, "RGB", blend_node, "AdditionalNormal (V3)")

    flat   = const3(0.5, 0.5, 1.0, -500, -430)   # flat normal in 0-1 space
    lrp    = lerp(                  -250, -530)
    cx(flat,       "",    lrp, "A")
    cx(blend_node, "",    lrp, "B")
    cx(p_normal_scl, "",  lrp, "Alpha")
    normal_out = lrp
else:
    unreal.log_warning("BlendAngleCorrectedNormals not found – using single normal layer.")
    normal_out = norm1

# ── Wire to material root pins ────────────────────────────────────────────────
cp(p_base_color,  "RGB", P.MP_BASE_COLOR)
cp(p_roughness,   "",    P.MP_ROUGHNESS)
cp(p_specular,    "",    P.MP_SPECULAR)
cp(normal_out,    "",    P.MP_NORMAL)
cp(const1(0.0, -1800, -1000), "", P.MP_METALLIC)

# ── SingleLayerWaterMaterialOutput node ──────────────────────────────────────
slw = M.create_material_expression(
    mat, unreal.MaterialExpressionSingleLayerWaterMaterialOutput, 300, -300)
cx(p_scatter,     "RGB", slw, "ScatteringCoefficients")
cx(p_absorb,      "RGB", slw, "AbsorptionCoefficients")
cx(p_phase_g,     "",    slw, "PhaseG")
cx(p_color_scale, "",    slw, "ColorScaleBehindWater")

# ── Save ──────────────────────────────────────────────────────────────────────
unreal.EditorAssetLibrary.save_asset(mat.get_path_name())
unreal.log("✓ M_SingleLayerWater created at " + mat.get_path_name())
