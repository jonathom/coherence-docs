import pytest
import geopandas as gpd

from util import search_for_reference, create_gpd_for_scene, list_products_by_time

def test_list_products_by_time():
    days_list = ["21", "30"]
    month_path = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/08"
    expected_result = ["/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/08/21/S1A_IW_SLC__1SDV_20210821T174107_20210821T174134_039331_04A51D_E85D/S1A_IW_SLC__1SDV_20210821T174107_20210821T174134_039331_04A51D_E85D.zip", "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/08/21/S1A_IW_SLC__1SDV_20210821T174132_20210821T174159_039331_04A51D_7184/S1A_IW_SLC__1SDV_20210821T174132_20210821T174159_039331_04A51D_7184.zip", "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/08/21/S1B_IW_SLC__1SDV_20210821T054128_20210821T054155_028340_0361A3_AB8D/S1B_IW_SLC__1SDV_20210821T054128_20210821T054155_028340_0361A3_AB8D.zip", "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/08/21/S1B_IW_SLC__1SDV_20210821T054152_20210821T054220_028340_0361A3_6100/S1B_IW_SLC__1SDV_20210821T054152_20210821T054220_028340_0361A3_6100.zip", "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/08/21/S1B_IW_SLC__1SDV_20210821T054217_20210821T054244_028340_0361A3_44E5/S1B_IW_SLC__1SDV_20210821T054217_20210821T054244_028340_0361A3_44E5.zip"]
                       # "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/08/30/S1A_IW_SLC__1SDV_20210830T060647_20210830T060714_039455_04A951_7C4E/S1A_IW_SLC__1SDV_20210830T060647_20210830T060714_039455_04A951_7C4E.zip", "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/08/30/S1A_IW_SLC__1SDV_20210830T060712_20210830T060739_039455_04A951_1AC8/S1A_IW_SLC__1SDV_20210830T060712_20210830T060739_039455_04A951_1AC8.zip"]
    fun_result = list_products_by_time("2021/08/21", "2021/08/22")
    fun_result = list(map(lambda x: x.absolute().as_posix(), fun_result))
    assert len(fun_result) == len(expected_result)
    assert set(fun_result) == set(expected_result)
    

def test_list_products_by_time_one_month():
    start = "2021/04/04"
    end = "2021/04/08"
    expected = 18
    products = list_products_by_time(start, end)
    assert len(products) == expected
    
    
def test_list_products_by_time_two_months():
    start = "2017/06/28"
    end = "2017/07/04"
    path = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/"
    expected = 18 # usually 18
    products = list_products_by_time(start, end, path)
    assert len(products) == expected
    
    
def test_search_for_reference_S1A():
    scene_gpd = create_gpd_for_scene(path = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/04/25/S1A_IW_SLC__1SDV_20210425T172448_20210425T172515_037610_046FB2_F6AB/S1A_IW_SLC__1SDV_20210425T172448_20210425T172515_037610_046FB2_F6AB.zip")
    ref_gpd = gpd.read_file("reference_bursts.geojson")
    references = search_for_reference(scene_gpd, ref_gpd)
    assert set(references) == set(["7AA0"])
    
    
def test_search_for_reference_S1B_none():
    scene_gpd = create_gpd_for_scene(path = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/04/17/S1B_IW_SLC__1SDV_20210417T174054_20210417T174130_026510_032A4B_DA8B/S1B_IW_SLC__1SDV_20210417T174054_20210417T174130_026510_032A4B_DA8B.zip")
    ref_gpd = gpd.read_file("reference_bursts.geojson")
    references = search_for_reference(scene_gpd, ref_gpd)
    print(references)
    assert references == {}
    
    
def test_search_for_reference_S1B_one():
    scene_gpd = create_gpd_for_scene(path = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/04/24/S1B_IW_SLC__1SDV_20210424T173139_20210424T173205_026612_032D91_05D2/S1B_IW_SLC__1SDV_20210424T173139_20210424T173205_026612_032D91_05D2.zip")
    ref_gpd = gpd.read_file("reference_bursts.geojson")
    references = search_for_reference(scene_gpd, ref_gpd)
    assert set(references) == set(["14F6"])
    
    
def test_search_for_reference_S1B_two():
    scene_gpd = create_gpd_for_scene(path = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2021/04/16/S1B_IW_SLC__1SDV_20210416T054955_20210416T055022_026488_03298E_BA6F/S1B_IW_SLC__1SDV_20210416T054955_20210416T055022_026488_03298E_BA6F.zip")
    ref_gpd = gpd.read_file("reference_bursts.geojson")
    references = search_for_reference(scene_gpd, ref_gpd)
    assert set(references) == set(["9F0A", "7BC8"])
    
    
def test_search_for_reference_S1B_old():
    scene_gpd = create_gpd_for_scene(path = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/IW/DV/2017/11/28/S1B_IW_SLC__1SDV_20171128T173948_20171128T174015_008485_00F0A7_30C7/S1B_IW_SLC__1SDV_20171128T173948_20171128T174015_008485_00F0A7_30C7.zip")
    ref_gpd = gpd.read_file("reference_bursts.geojson")
    references = search_for_reference(scene_gpd, ref_gpd)
    assert set(references) == set(["AAC4"])