"""
CreateSingleLayerWater.py
--------------------------
Unreal Engine 5.6 Python script that procedurally builds a physically-based
Single Layer Water material (M_SingleLayerWater) inside the editor.

How to run
----------
1. Enable the Python Editor Script Plugin (Edit > Plugins > Python Editor Script Plugin).
2. Open the Output Log (Window > Output Log).
3. In the Output Log, switch the input mode to "Python".
4. Paste the full path to this file and press Enter:
       exec(open("D:/YourProject/WaterMaterial/CreateSingleLayerWater.py").read())
   -- or use the menu:
       File > Execute Python Script > select this file.

What is created
---------------
Asset path : /Game/Materials/Water/M_SingleLayerWater

Material properties
-------------------
  Shading Model : Single Layer Water
  Blend Mode    : Opaque
  Domain        : Surface

Exposed parameters (tweak in Material Instance or the material editor)
----------------------------------------------------------------------
  ShallowWaterColor       (Vector4) – base colour of the water surface
  ScatteringCoefficients  (Vector3) – sub-surface light scattering per channel
  AbsorptionCoefficients  (Vector3) – light absorption per channel
  NormalMap               (Texture2D) – normal map sampled twice at different
                                        scales / speeds to simulate waves
  NormalScale             (Scalar)  – master normal intensity
  WavePanSpeed1           (Scalar)  – panning speed of the large-scale wave layer
  WavePanSpeed2           (Scalar)  – panning speed of the fine-scale wave layer
  WaveTiling1             (Scalar)  – UV tiling of layer 1
  WaveTiling2             (Scalar)  – UV tiling of layer 2
  Roughness               (Scalar)  – surface roughness (default 0.08)
  Specular                (Scalar)  – specular intensity  (default 0.5)
  PhaseG                  (Scalar)  – Henyey-Greenstein scattering phase (0-1)
  ColorScaleBehindWater   (Scalar)  – brightness scale for objects seen through
                                      the water (refraction strength)
"""

import unreal

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
MEL = unreal.MaterialEditingLibrary


def _param_vector(mat, name, default_color, x, y):
    """Create a VectorParameter expression."""
    expr = MEL.create_material_expression(
        mat, unreal.MaterialExpressionVectorParameter, x, y
    )
    expr.set_editor_property("parameter_name", name)
    expr.set_editor_property(
        "default_value",
        unreal.LinearColor(
            default_color[0], default_color[1], default_color[2],
            default_color[3] if len(default_color) > 3 else 1.0,
        ),
    )
    return expr


def _param_scalar(mat, name, default_value, x, y):
    """Create a ScalarParameter expression."""
    expr = MEL.create_material_expression(
        mat, unreal.MaterialExpressionScalarParameter, x, y
    )
    expr.set_editor_property("parameter_name", name)
    expr.set_editor_property("default_value", default_value)
    return expr


def _param_texture(mat, name, sampler_type, x, y):
    """Create a TextureSampleParameter2D expression."""
    expr = MEL.create_material_expression(
        mat, unreal.MaterialExpressionTextureSampleParameter2D, x, y
    )
    expr.set_editor_property("parameter_name", name)
    expr.set_editor_property("sampler_type", sampler_type)
    return expr


def _const(mat, value, x, y):
    """Create a Constant expression."""
    expr = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant, x, y)
    expr.set_editor_property("r", float(value))
    return expr


def _connect(from_expr, from_pin, to_expr, to_pin):
    MEL.connect_material_expressions(from_expr, from_pin, to_expr, to_pin)


def _connect_prop(from_expr, from_pin, mat_prop):
    MEL.connect_material_property(from_expr, from_pin, mat_prop)


# ---------------------------------------------------------------------------
# Main creation function
# ---------------------------------------------------------------------------
def create_single_layer_water_material(
    asset_name="M_SingleLayerWater",
    asset_path="/Game/Materials/Water",
):
    # ------------------------------------------------------------------
    # 1. Create the material asset
    # ------------------------------------------------------------------
    full_path = f"{asset_path}/{asset_name}"

    # Delete existing asset if present so we can recreate cleanly
    if unreal.EditorAssetLibrary.does_asset_exist(full_path):
        unreal.EditorAssetLibrary.delete_asset(full_path)
        unreal.log(f"Deleted existing asset: {full_path}")

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat = asset_tools.create_asset(
        asset_name, asset_path, unreal.Material, unreal.MaterialFactoryNew()
    )

    if not mat:
        unreal.log_error("Failed to create material asset!")
        return None

    # ------------------------------------------------------------------
    # 2. Material-level settings
    # ------------------------------------------------------------------
    mat.set_editor_property(
        "shading_model", unreal.MaterialShadingModel.MSM_SINGLE_LAYER_WATER
    )
    mat.set_editor_property("blend_mode", unreal.EBlendMode.BLEND_OPAQUE)
    mat.set_editor_property("two_sided", False)

    # ------------------------------------------------------------------
    # 3. Parameters
    # ------------------------------------------------------------------
    #  Column layout (x positions)
    COL_FAR   = -2000
    COL_MID   = -1400
    COL_NEAR  = -900
    COL_SLW   = 300

    # Shallow water colour -> BaseColor
    p_shallow = _param_vector(mat, "ShallowWaterColor",
                              [0.01, 0.12, 0.22, 1.0], COL_FAR, -800)

    # Scattering / absorption for the SLW output node
    p_scatter = _param_vector(mat, "ScatteringCoefficients",
                              [0.05, 0.14, 0.28, 1.0], COL_FAR, -580)
    p_absorb  = _param_vector(mat, "AbsorptionCoefficients",
                              [0.45, 0.18, 0.07, 1.0], COL_FAR, -360)

    # Scalar params
    p_roughness      = _param_scalar(mat, "Roughness",            0.08, COL_FAR, -140)
    p_specular       = _param_scalar(mat, "Specular",             0.5,  COL_FAR,  40)
    p_phase_g        = _param_scalar(mat, "PhaseG",               0.8,  COL_FAR,  220)
    p_color_scale    = _param_scalar(mat, "ColorScaleBehindWater", 1.0, COL_FAR,  400)
    p_normal_scale   = _param_scalar(mat, "NormalScale",           1.0, COL_FAR,  580)
    p_wave_speed1    = _param_scalar(mat, "WavePanSpeed1",         0.02, COL_FAR,  760)
    p_wave_speed2    = _param_scalar(mat, "WavePanSpeed2",         0.01, COL_FAR,  940)
    p_wave_tiling1   = _param_scalar(mat, "WaveTiling1",           2.0, COL_FAR, 1120)
    p_wave_tiling2   = _param_scalar(mat, "WaveTiling2",           4.0, COL_FAR, 1300)

    # Normal map texture parameter (assign a default normal map in the editor
    # or in a Material Instance; flat normal 0,0,1 is fine as placeholder)
    p_normal_tex = _param_texture(
        mat, "NormalMap",
        unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL,
        COL_MID, -400,
    )

    # ------------------------------------------------------------------
    # 4. Wave Layer 1  –  large-scale, slow pan
    #    TexCoord scaled by WaveTiling1, panned by WavePanSpeed1
    # ------------------------------------------------------------------
    tc1 = MEL.create_material_expression(
        mat, unreal.MaterialExpressionTextureCoordinate, COL_MID, -800
    )

    # Multiply TexCoord by WaveTiling1
    mul_tc1 = MEL.create_material_expression(
        mat, unreal.MaterialExpressionMultiply, COL_MID - 200, -800
    )
    _connect(tc1, "", mul_tc1, "A")
    _connect(p_wave_tiling1, "", mul_tc1, "B")

    # Panner for layer 1
    pan1 = MEL.create_material_expression(mat, unreal.MaterialExpressionPanner, COL_MID, -680)
    pan1.set_editor_property("const_speed_x",  0.0)   # direction baked into speed params
    pan1.set_editor_property("const_speed_y",  0.0)
    _connect(mul_tc1, "", pan1, "Coordinate")
    _connect(p_wave_speed1, "", pan1, "Speed")

    # Sample normal map – layer 1
    ns1 = _param_texture(mat, "NormalMap", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL,
                         COL_NEAR, -800)
    _connect(pan1, "", ns1, "UVs")

    # ------------------------------------------------------------------
    # 5. Wave Layer 2  –  fine-scale, slightly faster counter-pan
    # ------------------------------------------------------------------
    tc2 = MEL.create_material_expression(
        mat, unreal.MaterialExpressionTextureCoordinate, COL_MID, -200
    )

    mul_tc2 = MEL.create_material_expression(
        mat, unreal.MaterialExpressionMultiply, COL_MID - 200, -200
    )
    _connect(tc2, "", mul_tc2, "A")
    _connect(p_wave_tiling2, "", mul_tc2, "B")

    pan2 = MEL.create_material_expression(mat, unreal.MaterialExpressionPanner, COL_MID, -80)
    pan2.set_editor_property("const_speed_x", 0.0)
    pan2.set_editor_property("const_speed_y", 0.0)
    _connect(mul_tc2, "", pan2, "Coordinate")
    _connect(p_wave_speed2, "", pan2, "Speed")

    ns2 = _param_texture(mat, "NormalMap", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL,
                         COL_NEAR, -200)
    _connect(pan2, "", ns2, "UVs")

    # ------------------------------------------------------------------
    # 6. Blend normals with BlendAngleCorrectedNormals material function
    # ------------------------------------------------------------------
    BLEND_FUNC_PATH = (
        "/Engine/Functions/Engine_MaterialFunctions02/Utility/BlendAngleCorrectedNormals"
    )
    blend_func_asset = unreal.load_asset(BLEND_FUNC_PATH)

    normal_final = None  # expression that feeds Normal pin

    if blend_func_asset:
        blend_node = MEL.create_material_expression(
            mat, unreal.MaterialExpressionMaterialFunctionCall, COL_NEAR + 400, -500
        )
        blend_node.set_editor_property("material_function", blend_func_asset)
        _connect(ns1, "RGB", blend_node, "BaseNormal (V3)")
        _connect(ns2, "RGB", blend_node, "AdditionalNormal (V3)")

        # Scale blended normal by NormalScale via FlattenNormal or simple lerp
        # Use Lerp(float3(0,0,1), blended, NormalScale) to drive intensity
        lerp_n = MEL.create_material_expression(
            mat, unreal.MaterialExpressionLinearInterpolate, COL_NEAR + 650, -500
        )
        flat_n = MEL.create_material_expression(
            mat, unreal.MaterialExpressionConstant3Vector, COL_NEAR + 450, -380
        )
        flat_n.set_editor_property("constant", unreal.LinearColor(0.5, 0.5, 1.0, 1.0))  # flat normal
        _connect(flat_n,    "", lerp_n, "A")
        _connect(blend_node, "", lerp_n, "B")
        _connect(p_normal_scale, "", lerp_n, "Alpha")
        normal_final = lerp_n
    else:
        # Fallback – just use ns1 directly
        unreal.log_warning(
            "BlendAngleCorrectedNormals function not found; falling back to single normal layer."
        )
        normal_final = ns1

    # ------------------------------------------------------------------
    # 7. Wire parameters to material root pins
    # ------------------------------------------------------------------
    _connect_prop(p_shallow,   "RGB", unreal.EMaterialProperty.MP_BASE_COLOR)
    _connect_prop(p_roughness, "",    unreal.EMaterialProperty.MP_ROUGHNESS)
    _connect_prop(p_specular,  "",    unreal.EMaterialProperty.MP_SPECULAR)
    _connect_prop(normal_final, "",   unreal.EMaterialProperty.MP_NORMAL)

    # Metallic = 0 (water is a dielectric)
    metallic_zero = _const(mat, 0.0, COL_FAR + 200, -1000)
    _connect_prop(metallic_zero, "", unreal.EMaterialProperty.MP_METALLIC)

    # ------------------------------------------------------------------
    # 8. SingleLayerWaterMaterialOutput node
    #    This node captures the volumetric water parameters that the
    #    renderer uses for sub-surface scattering / absorption.
    # ------------------------------------------------------------------
    slw_out = MEL.create_material_expression(
        mat, unreal.MaterialExpressionSingleLayerWaterMaterialOutput,
        COL_SLW, -300
    )

    _connect(p_scatter,    "RGB", slw_out, "ScatteringCoefficients")
    _connect(p_absorb,     "RGB", slw_out, "AbsorptionCoefficients")
    _connect(p_phase_g,    "",    slw_out, "PhaseG")
    _connect(p_color_scale, "",   slw_out, "ColorScaleBehindWater")

    # ------------------------------------------------------------------
    # 9. Save
    # ------------------------------------------------------------------
    unreal.EditorAssetLibrary.save_asset(mat.get_path_name())
    unreal.log(
        f"\n=== Single Layer Water material created successfully ===\n"
        f"    Path : {mat.get_path_name()}\n"
        f"Open the asset in the Material Editor to assign a normal map texture\n"
        f"and fine-tune the exposed parameters.\n"
    )
    return mat


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    create_single_layer_water_material()
