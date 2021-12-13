# create shapefiles from S1 files based on a catalgoue search
from terracatalogueclient import Catalogue
import datetime as dt
import stsa

# processes only VV

# define name of result
name = "testRun_01"

catalogue = Catalogue()

bbox = {"west": 4.38, "south": 51.21, "east": 4.42, "north": 51.24}

# give one date, find closest acqusition before and after
event = dt.date(2021, 10, 15) # input
before = event - dt.timedelta(days = 6)

print("[CATALOGUE]: starting search for scenes...")

# first search
cat_before = catalogue.get_products(
	"urn:eop:VITO:CGS_S1_SLC_L1",
	start = before,
	end = event,
	bbox = bbox
)

prod_before = {"date": None, "id": None, "path": None, 
			"orbitDirection": None, "relativeOrbitNumber": None}

# find the product closest to event date, save direction and rel orbit
for p in cat_before:
	path = p.data[0].href 
	iw_index = path.index("IW")
	vm_path = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/" + path[iw_index:]

	if prod_before["date"] is None:
		prod_before["date"] = p.beginningDateTime
		prod_before["id"] = p.id
		prod_before["path"] = vm_path
		prod_before["orbitDirection"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["orbitDirection"]
		prod_before["relativeOrbitNumber"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["relativeOrbitNumber"]
	else:
		if p.beginningDateTime > prod_before["date"]:
			prod_before["date"] = p.beginningDateTime
			prod_before["id"] = p.id
			prod_before["path"] = vm_path
			prod_before["orbitDirection"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["orbitDirection"]
			prod_before["relativeOrbitNumber"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["relativeOrbitNumber"]
		else:
			pass

print("[PROD_BEFORE]: ", prod_before)

print("[CATALOGUE]: found first scene from date: ", prod_before["date"], " & path: ", prod_before["path"])

first_scene_date = prod_before["date"]
after = first_scene_date + dt.timedelta(days = 30)

# quary for second product given the direction and rel orbit
cat_after = catalogue.get_products(
	"urn:eop:VITO:CGS_S1_SLC_L1",
	start = first_scene_date + dt.timedelta(days = 1),
	end = after,
	bbox = bbox,
	orbitDirection = prod_before["orbitDirection"],
	relativeOrbitNumber = prod_before["relativeOrbitNumber"]
)

prod_after = {"date": None, "id": None, "path": None}

# find the closest one to event date
for p in cat_after:	
	path = p.data[0].href 
	iw_index = path.index("IW")
	vm_path = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/" + path[iw_index:]
	
	ana_split = stsa.TopsSplitAnalyzer(target_subswaths=['iw1', 'iw2', 'iw3'])
	ana_split.load_data(zip_path = vm_path)
	splithere = vm_path.rfind('/') + 1
	ana_split.to_shapefile('/home/jonathanbahlmann/Public/scenes/stsa_' + vm_path[splithere:] + '.shp')
	
	if prod_after["date"] is None:
		prod_after["date"] = p.beginningDateTime
		prod_after["id"]  = p.id

		prod_after["path"] = vm_path
	else:
		if p.beginningDateTime < prod_after["date"]:
			prod_after["date"] = p.beginningDateTime
			prod_after["id"] = p.id
			prod_after["path"] = vm_path
		else:
			pass
			
print("[CATALOGUE]: found matching scene from date: ", prod_after["date"], " & path: ", prod_after["path"])

# s1-tops-split-analyzer



	# ana_split_1.load_data(zip_path = )
	# ana_split_1.to_shapefile('/home/jonathanbahlmann/Public/scenes/stsa_13_10.shp')
	# ana_split_1.to_json('/home/jonathanbahlmann/Public/scenes/stsa_13_10.geojson')


# ana_split_2 = stsa.TopsSplitAnalyzer(target_subswaths=['iw1', 'iw2', 'iw3'])
# ana_split_2.load_data(zip_path = prod_after["path"])

# ana_split_2.to_shapefile('/home/jonathanbahlmann/Public/scenes/stsa_19_10.shp')
# ana_split_2.to_json('/home/jonathanbahlmann/Public/scenes/stsa_19_10.geojson')
