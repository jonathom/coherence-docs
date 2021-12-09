from terracatalogueclient import Catalogue
import datetime as dt

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
	if prod_before["date"] is None:
		prod_before["date"] = p.beginningDateTime
		prod_before["id"]  = p.id
		path = p.data[0].href 
		iw_index = path.index("IW")
		prod_before["path"] = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/" + path[iw_index:]
		prod_before["orbitDirection"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["orbitDirection"]
		prod_before["relativeOrbitNumber"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["relativeOrbitNumber"]
	else:
		if p.beginningDateTime > prod_before["date"]:
			prod_before["date"] = p.beginningDateTime
			prod_before["id"] = p.id
			path = p.data[0].href 
			iw_index = path.index("IW")
			prod_before["path"] = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/" + path[iw_index:]
			prod_before["orbitDirection"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["orbitDirection"]
			prod_before["relativeOrbitNumber"] = p.properties["acquisitionInformation"][1]["acquisitionParameters"]["relativeOrbitNumber"]
		else:
			pass

print("[PROD_BEFORE]: ", prod_before)

print("[CATALOGUE]: found first scene from date: ", prod_before["date"], " & path: ", prod_before["path"])

first_scene_date = prod_before["date"]
after = first_scene_date + dt.timedelta(days = 12)

# quary for second product given the direction and rel orbit
cat_after = catalogue.get_products(
	"urn:eop:VITO:CGS_S1_SLC_L1",
	start = first_scene_date + dt.timedelta(days = 10),
	end = after,
	bbox = bbox,
	orbitDirection = prod_before["orbitDirection"],
	relativeOrbitNumber = prod_before["relativeOrbitNumber"]
)

prod_after = {"date": None, "id": None, "path": None}

# find the closest one to event date
for p in cat_after:		
	if prod_after["date"] is None:
		prod_after["date"] = p.beginningDateTime
		prod_after["id"]  = p.id
		path = p.data[0].href 
		iw_index = path.index("IW")
		prod_after["path"] = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/" + path[iw_index:]
	else:
		if p.beginningDateTime < prod_after["date"]:
			prod_after["date"] = p.beginningDateTime
			prod_after["id"] = p.id
			path = p.data[0].href
			iw_index = path.index("IW")
			prod_after["path"] = "/data/MTDA/CGS_S1/CGS_S1_SLC_L1/" + path[iw_index:]
		else:
			pass
			
print("[CATALOGUE]: found matching scene from date: ", prod_after["date"], " & path: ", prod_after["path"])