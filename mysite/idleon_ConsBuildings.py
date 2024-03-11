import json
from consts import getSpecificSkillLevelsList
from models import AdviceSection, AdviceGroup, Advice
from utils import pl, get_logger
from flask import g as session_data

logger = get_logger(__name__)

def parseConsBuildingstoLists(inputJSON):
    consBuildingsList = json.loads(inputJSON["Tower"])  #expected type of list
    #logger.debug(f"TYPE CHECK consBuildingsList: {type(consBuildingsList)}: {consBuildingsList}")
    return consBuildingsList

def getBuildingNameFromIndex(inputNumber):
    towerList = ["3D Printer", "Talent Book Library", "Death Note", "Salt Lick", "Chest Space", "Cost Cruncher", "Trapper Drone", "Automation Arm", "Atom Collider", "Pulse Mage", "Fireball Lobber", "Boulder Roller", "Frozone Malone", "Stormcaller", "Party Starter", "Kraken Cosplayer", "Poisonic Elder", "Voidinator", "Woodular Shrine", "Isaccian Shrine", "Crystal Shrine", "Pantheon Shrine", "Clover Shrine", "Summereading Shrine", "Crescent Shrine", "Undead Shrine", "Primordial Shrine"]
    try:
        inputNumber = int(inputNumber)
        return towerList[inputNumber]
    except:
        return "UnknownBuilding"+str(inputNumber)

def getBuildingImageNameFromIndex(inputNumber):
    towerImageNameList = ["three-d-printer", "talent-book-library", "death-note", "salt-lick", "chest-space", "cost-cruncher", "critter-drone",
                          "automation-arm", "atom-collider", "pulse-mage", "fireball-lobber", "boulder-roller", "frozone-malone", "stormcaller",
                          "party-starter", "kraken-cosplayer", "poisonic-elder", "voidinator", "woodular-shrine", "isaccian-shrine", "crystal-shrine",
                          "pantheon-shrine", "clover-shrine", "summereading-shrine", "crescent-shrine", "undead-shrine", "primordial-shrine"]
    try:
        inputNumber = int(inputNumber)
        return towerImageNameList[inputNumber]
    except:
        return "UnknownBuilding"+str(inputNumber)

def getInfluencers(inputJSON):
    #Honker Vial level
    try:
        honkerVialLevel = inputJSON["CauldronInfo"][4]["40"]  #expected type of int
        logger.debug(f"TYPE CHECK honkerVialLevel: {type(honkerVialLevel)}: {honkerVialLevel}")
    except Exception as reason:
        honkerVialLevel = 0
        logger.exception(f"Unable to retrieve honkerVialLevel: {reason}")

    #Boulder Roller level
    try:
        poisonicLevel = json.loads(inputJSON["Tower"])[16]  #expected type of int
        #logger.debug(f"TYPE CHECK poisonicLevel: {type(poisonicLevel)}: poisonicLevel")
    except Exception as reason:
        poisonicLevel = 0
        logger.exception(f"Unable to retrieve poisonicLevel: {reason}")

    #Other?
    atomCarbon = False
    if session_data.account.construction_mastery_unlocked:
        consMastery = True
    else:
        consMastery = False

    try:
        carbonLevel = inputJSON["Atoms"][5]
        if carbonLevel >= 1:
            atomCarbon = True
    except Exception as reason:
        logger.exception(f"Unable to find Atom Collider Carbon level: {reason}")
    results = [(consMastery or atomCarbon), honkerVialLevel, poisonicLevel]
    #logger.debug(f"Influencer results: EitherBuff: {results[0]}, Honker Vial Level: {results[1]}, Poisonic Tower Level: {results[2]}")
    return results

def setConsBuildingsProgressionTier(inputJSON, progressionTiersPreBuffs, progressionTiersPostBuffs, characterDict):
    building_AdviceDict = {}
    building_AdviceGroupDict = {}
    building_AdviceSection = AdviceSection(
        name="Buildings",
        tier="",
        header="Recommended Construction Buildings priorities for Trimmed Slots",
        picture="Construction_Table.gif",
        collapse=False
    )
    constructionLevelsList = getSpecificSkillLevelsList(inputJSON, len(characterDict), "Construction")
    if max(constructionLevelsList) < 1:
        building_AdviceSection.header = "Come back after unlocking the Construction skill in World 3!"
        return building_AdviceSection

    maxBuildingsPerGroup = 10
    playerBuildings = parseConsBuildingstoLists(inputJSON)
    influencers = getInfluencers(inputJSON)
    hasBuffs = influencers[0]
    if hasBuffs:
        #maxLevelList = [10, 201, 51, 10, 25, 60, 45, 5, 200,    140, 140, 140, 140, 140, 140, 140, 140, 140,   200, 200, 200, 200, 200, 200, 200, 200, 200]  # these are true max, not recommended max
        maxLevelList = [10, 101, 51, 10, 25, 60, 20, 5, 200,    70, 70, 70, 70, 70, 70, 75, 75, 30,             200, 200, 200, 200, 200, 200, 200, 200, 200]  # the recommended maxes
        #logger.debug(" Either Construction Mastery and Wizard Atom found. Setting maxLevelList to PostBuff.")
    else:
        maxLevelList = [10, 101, 51, 10, 25, 60, 15, 5, 200,    50, 50, 50, 50, 50, 50, 50, 50, 30,             100, 100, 100, 100, 100, 100, 100, 100, 100]
        #logger.debug("ConsBuildings.setConsBuildingsProgressionTier~ INFO Setting maxLevelList to PreBuff.")

    # Make adjustments to tiers based on other influencers
    # 1) If any building is level 0, it gets promoted to SS tier
    buildingCounter = 0
    while buildingCounter < len(maxLevelList):
        #logger.debug(f"Is player level {playerBuildings[buildingCounter]} equal to 0 for Tower {buildingCounter} ({getBuildingNameFromIndex(buildingCounter)}): {playerBuildings[buildingCounter] == 0}")
        if playerBuildings[buildingCounter] == 0:
            maxLevelList[buildingCounter] = 1  #With a max recommended level of 1
            for tier in progressionTiersPostBuffs:
                if buildingCounter in tier[2] and tier[1] != "SS":
                    tier[2].remove(buildingCounter)  #Remove that building from any other non-SS tier.
                    progressionTiersPostBuffs[1][2].append(buildingCounter)
                    logger.debug(f"Level 0 building detected. Removing {getBuildingNameFromIndex(buildingCounter)} from POSTBuff {tier[1]} and adding to SS with max level 1 instead.")
            for tier in progressionTiersPreBuffs:
                if buildingCounter in tier[2] and tier[1] != "SS":
                    tier[2].remove(buildingCounter)  #Remove that building from any other non-SS tier.
                    progressionTiersPreBuffs[1][2].append(buildingCounter)
                    logger.debug(f"Level 0 building detected. Removing {getBuildingNameFromIndex(buildingCounter)} from PREBuff {tier[1]} and adding to SS with max level 1 instead.")
        buildingCounter += 1

    # 2) Honker vial is 12+ OR Trapper Drone is 20+, drop Trapper Drone priority
    if influencers[1] >= 12 or playerBuildings[6] >= 20:
        try:
            progressionTiersPostBuffs[2][2].remove(6)  #Remove Trapper Drone from S Tier
            progressionTiersPostBuffs[6][2].append(6)  #Add Trapper Drone to D tier
            if hasBuffs:
                maxLevelList[6] = 50
            #logger.debug("Successfully moved Trapper Drone from PostBuff S to D tier and changed level from 20 to 50")
        except Exception as reason:
            logger.exception(f"Could not remove Trapper Drone from PostBuff S tier: {reason}")

    # 3) #Poisonic level 20+, drop Boulder Roller priority
    if influencers[2] >= 20:
        try:
            #PreBuffs
            progressionTiersPreBuffs[2][2].remove(11)  #Remove Boulder Roller from S tier
            progressionTiersPreBuffs[6][2].append(11)  #Add Boulder Roller to D tier
            #logger.debug("Successfully moved Boulder Roller from PreBuff S to D tier because Poisonic 20+")
            #PostBuffs
            progressionTiersPostBuffs[2][2].remove(11)  #Remove Boulder Roller from S tier
            progressionTiersPostBuffs[3][2].append(11)  #Add Boulder Roller to A tier
            #logger.debug("Successfully moved Boulder Roller from PostBuff S to A tier because Poisonic 20+")
        except Exception as reason:
            logger.exception(f"Could not move Boulder Roller from S tier in one or both tierlists: {reason}")

    # 4) Talent Library Book 101+, drop priority
    if playerBuildings[1] >= 101:
        try:
            progressionTiersPostBuffs[2][2].remove(1)  #Remove from S tier
            progressionTiersPostBuffs[5][2].append(1)  #Add to C tier
            if hasBuffs:
                maxLevelList[1] = 201
            #logger.debug("Successfully moved 101+ Talent Library Book from PostBuff A to C tier.")
        except Exception as reason:
            logger.exception(f"Could not move 101+ Talent Library Book from PostBuff A tier to C tier: {reason}")

    # 5) #Basic Towers to 70, drop priority
    for towerIndex in [9,10,11,12,13,14]:
        if playerBuildings[towerIndex] >= 70:
            try:
                progressionTiersPostBuffs[3][2].remove(towerIndex)  #Remove from A tier
                progressionTiersPostBuffs[5][2].append(towerIndex)  #Add to C tier
                if hasBuffs:
                    maxLevelList[towerIndex] = 140
                #logger.info(f"Successfully moved 70+ basic tower from PostBuff A to C tier: {getBuildingNameFromIndex(towerIndex)})
            except Exception as reason:
                logger.exception(f"Could not move 70+ basic tower {getBuildingNameFromIndex(towerIndex)} from PostBuff A tier to C tier: {reason}")

    # 6) Fancy Towers to 75, drop priority
    for towerIndex in [15,16]:
        if playerBuildings[towerIndex] >= 75:
            try:
                progressionTiersPostBuffs[2][2].remove(towerIndex)  #Remove from S tier
                progressionTiersPostBuffs[4][2].append(towerIndex)  #Add to B tier
                if hasBuffs:
                    maxLevelList[towerIndex] = 140
                #logger.debug(f"Successfully moved 75+ fancy tower {getBuildingNameFromIndex(towerIndex)} from PostBuff S to B tier")
            except Exception as reason:
                logger.exception(f"EXCEPTION Could not move 75+ fancy tower {getBuildingNameFromIndex(towerIndex)} from PostBuff S tier to B tier: {reason}")

    # 7) Voidinator to 30, drop priority
    if playerBuildings[17] >= 30:  #Voidinator scaling is very bad
        try:
            progressionTiersPreBuffs[4][2].remove(17)  #Remove from PreBuff B tier
            progressionTiersPreBuffs[5][2].append(17)  #Add to C tier
            progressionTiersPostBuffs[3][2].remove(17)  #Remove from PostBuff A tier
            progressionTiersPostBuffs[5][2].append(17)  #Add to C tier
            if hasBuffs:
                maxLevelList[17] = 140
            #logger.debug("Successfully moved 30+ Voidinator from A/B to C tier in both tierlists")
        except Exception as reason:
            logger.exception(f"Could not move 30+ Voidinator from A/B to C tier in both tierlists: {reason}")

    # Decide which tierset to use
    if influencers[0] == True:  #Has either Construction Mastery or the Wizard atom
        progressionTiers = progressionTiersPostBuffs
        #logger.debug("Either Construction Mastery or Wizard Atom found. Setting ProgressionTiers to PostBuff.")
    else:
        progressionTiers = progressionTiersPreBuffs
        #logger.debug("Setting ProgressionTiers to PreBuff.")

    #tier[0] = int tier
    #tier[1] = str Tier name
    #tier[2] = list of ints of tower indexes
    #tier[3] = str tower notes
    #tier[4] = str tier notes
    tierNamesList = []
    for counter in range(0, len(progressionTiers)):
        building_AdviceDict[counter] = []
        tierNamesList.append(progressionTiers[counter][1])
        for recommendedBuilding in progressionTiers[counter][2]:
            try:
                #logger.debug(f"{progressionTiers[counter][1]} Tier: Building {recommendedBuilding} ({getBuildingNameFromIndex(recommendedBuilding)}): Cleared if {maxLevelList[recommendedBuilding]} <= {playerBuildings[recommendedBuilding]}. Cleared= {maxLevelList[recommendedBuilding] <= playerBuildings[recommendedBuilding]}")
                if maxLevelList[recommendedBuilding] > playerBuildings[recommendedBuilding]:
                    if len(building_AdviceDict[counter]) < maxBuildingsPerGroup:
                        #logger.debug(f"Adding advice for {getBuildingNameFromIndex(recommendedBuilding)} to {counter}")
                        building_AdviceDict[counter].append(Advice(label=getBuildingNameFromIndex(recommendedBuilding),
                                                                   picture_class=getBuildingImageNameFromIndex(recommendedBuilding),
                                                                   progression=str(playerBuildings[recommendedBuilding]),
                                                                   goal=str(maxLevelList[recommendedBuilding]))
                                                            )
                else:
                    #logger.debug(f"{progressionTiers[counter][1]} Tier: Max met for {getBuildingNameFromIndex(recommendedBuilding)}, not generating Advice")
                    continue
            except Exception as reason:
                logger.exception(f"ProgressionTier evaluation error. Counter = {counter}, recommendedBuilding = {recommendedBuilding}, Reason: {reason}")

    #Generate AdviceGroups
    for tierKey in building_AdviceDict.keys():
        building_AdviceGroupDict[tierKey] = AdviceGroup(
            tier="",
            pre_string=f"{str(tierNamesList[tierKey])} Tier",
            advices=building_AdviceDict[tierKey],
            post_string=""
        )
        if len(building_AdviceDict[tierKey]) == maxBuildingsPerGroup:
            building_AdviceGroupDict[tierKey].post_string = f"Up to {maxBuildingsPerGroup} remaining buildings shown"

    #Generate AdviceSection
    building_AdviceSection.groups = building_AdviceGroupDict.values()
    return building_AdviceSection
