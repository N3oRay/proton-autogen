# -----------------------------------------------------------------
# AppIDs connus pour des exécutables spécifiques, utilisés en dernier
# recours quand aucune détection automatique (env, appmanifest,
# steam_appid.txt) n'a abouti. Utile pour les jeux anciens copiés
# hors de leur bibliothèque Steam d'origine (GOG, backups, etc.).
# Clé : nom de fichier de l'exécutable (insensible à la casse).
# -----------------------------------------------------------------
KNOWN_APPIDS = {

    # ----------------------------------
    # PlayStation Publishing LLC -
    # ----------------------------------
    "GoW.exe": "1593500",                    # God of War
    "GoWR.exe": "2322010",                   # God of War Ragnarök
    "HorizonZeroDawn.exe": "1151640",        # Horizon Zero Dawn Complete Edition
    "HorizonZeroDawnRemastered.exe": "2561580", # Horizon Zero Dawn Remastered
    "HorizonForbiddenWest.exe": "2420110",   # Horizon Forbidden West Complete Edition
    "GhostOfTsushima.exe": "2215430",        # Ghost of Tsushima DIRECTOR'S CUT

    "Spider-Man.exe": "1817070",             # Marvel's Spider-Man Remastered
    "MilesMorales.exe": "1817190",           # Marvel's Spider-Man: Miles Morales
    "SpiderMan2.exe": "2651280",             # Marvel's Spider-Man 2

    "Ratchet.exe": "1895880",                # Ratchet & Clank: Rift Apart
    "Sackboy.exe": "1599660",                # Sackboy: A Big Adventure
    "Returnal.exe": "1649240",               # Returnal
    "DaysGone.exe": "1259420",               # Days Gone

    "tll.exe": "4198780",                # Uncharted: The Lost Legacy
    "u4.exe": "1659420",                # Uncharted: Legacy of Thieves Collection
    "tlou-i.exe": "1888930",           # The Last of Us Part I
    "tlou-i-l.exe": "1888930",           # The Last of Us Part I
    "tlou-ii.exe": "2531310",           # The Last of Us Part II Remastered
    "tlou2.exe": "2531310",             # The Last of Us Part II Remastered

    "Helldivers2.exe": "553850",             # HELLDIVERS 2
    "Helldivers.exe": "394360",              # HELLDIVERS™ Dive Harder Edition

    "Predator.exe": "1556200",               # Predator: Hunting Grounds
    "Concord.exe": "2443720",                # Concord
    "Marathon.exe": "3065800",               # Marathon
    "Kena.exe": "1954200",                   # Kena: Bridge of Spirits
    "UntilDawn.exe": "2172010",              # Until Dawn
    "TheLastOfUsPartI.exe": "1888930",       # The Last of Us Part I
    "TheLastOfUsPartII.exe": "2531310",      # The Last of Us Part II Remastered

    "StellarBlade.exe": "3486920",           # Stellar Blade
    # -----------------------------
    # Applications / Launchers / divers
    # -----------------------------
    "KTSYSVIEW.exe": "363110",          # NOBUNAGA'S AMBITION: Tendou with Power Up Kit
    "GRYPHLINK.exe": "4732690",         # Arknights: Endfield - Steam (à venir)
    "mimi_setup_en_prod_1.5_20250417.exe": "480",
    "GLOBAL_sg.exe": "480",             # À identifier
    "Vortex.exe": "1868050",    # Vortex — Endless Void Studios
    "UbisoftConnect.exe": "480",        # Ubisoft Connect
    "EAppInstaller.exe": "480",         # EA app installer
    "POWERCOLOR_KEYTONE.exe": "480",    # Utilitaire PowerColor
    "WeMod.exe": "480",                              # WeMod

    "Launcher.exe": "442080",                        # Riders of Icarus
    "Mir4S.exe": "1623660",                          # MIR4
    "lswebbroker.exe": "1934850",                    # 王牌对决 / LostSaga CN
    "icarus-101xp-micro-launcher.exe": "921940",     # Icarus Online
    "Launcher.exe": "1711430",                       # Riders of Icarus: SEA
    "YmirSteam-Win64-Shipping.exe": "4172530",       # Legend of YMIR

    "BlackVultures.exe": "3622280",                  # Black Vultures: Prey of Greed
    "Sindrel Song.exe": "1191860",                   # Memody: Sindrel Song
    "projectssshooter.exe": "3247350",               # Operation REMODE
    "Brain Hotel Remodeled.exe": "2648510",           # Brain Hotel: Remodeled
    "HouseFlipper.exe": "613100",                    # House Flipper

    "FINAL FANTASY.exe": "1173770",                  # FINAL FANTASY
    "FINAL FANTASY II.exe": "1173780",               # FINAL FANTASY II
    "FINAL FANTASY III.exe": "1173790",              # FINAL FANTASY III
    "FINAL FANTASY IV.exe": "1173800",               # FINAL FANTASY IV
    "FINAL FANTASY V.exe": "1173810",                # FINAL FANTASY V
    "FINAL FANTASY VI.exe": "1173820",               # FINAL FANTASY VI

    "ReviveAndProsper.exe": "2497310",                # R & P: Prologue
    "KILLlaKILL_IF.exe": "922500",                   # KILL la KILL -IF
    "Manhole.exe": "63630",                           # The Manhole: Masterpiece Edition
    "Game.exe": "1534590",                            # Farm Dungeons
    "SimShock2025Windows.exe": "3704810",             # SimShock2025
    "CricketCaptain.exe": "1975570",                 # Cricket Captain 2022
    "HomeDesignVR.exe": "2589880",                   # Home Design 3D VR
    "Little Merchant Legend.exe": "1939740",         # Little Merchant Legend
    "Real.exe": "2727700",                            # Real
    "Keystones.exe": "1027930",                       # Keystones
    "7 Wonders - Treasures of Seven.exe": "16030",   # 7 Wonders: Treasures of Seven
    "Everfall 2 Idle Dungeon RPG.exe": "4245410",   # Everfall 2: Idle Dungeon RPG
    "CatchTheThief.exe": "717760",                   # Catch the Thief, If you can!
    "Everfall Idle Dungeon RPG.exe": "4112810",      # Everfall: Idle Dungeon RPG
    "JunkyardTruck.exe": "1697880",                 # Junkyard Truck
    "SurvivalGame.exe": "1032120",                   # Stellar Survivor
    "Lorne.exe": "2172970",                          # Lorne

    # -----------------------------
    # Jeux
    # -----------------------------
    "World_of_warship.exe": "552990",   # World of Warships

    "Ra2.exe": "2229850",              # Command & Conquer: Red Alert 2
    "RA2MD.exe": "2229850",            # Command & Conquer: Yuri's Revenge
    "runme.exe": "17480",               # Command & Conquer: Red Alert 3
    "RA3EP1.exe": "24800",              # Command & Conquer: Red Alert 3 - Uprising
    "RA95.EXE": "2229840",              # Command & Conquer: Red Alert
    "RASETUP.EXE": "2229840",              # Command & Conquer: Red Alert
    "setup-00974-C&C_Alerte_Rouge-PCWin.exe": "2229840",              # Command & Conquer: Red Alert
    "ClientLauncherG.exe": "1213210",   # Command & Conquer Remastered Collection
    "OMGZ.exe": "259870",               # OMG Zombies!
    "The Red Exile.exe": "1751890",     # The Red Exile: Survival Horror
    "Darkest Dungeon II.exe": "1940340",# Darkest Dungeon II
    "Stratside.exe": "604990",          # Stratside
    "Catmaze.exe": "620220",            # Catmaze
    # -----------------------------
    # Atelier
    # -----------------------------
    "AtelierRorona.exe": "936180",               # Atelier Rorona DX
    "AtelierTotori.exe": "936190",               # Atelier Totori DX
    "AtelierMeruru.exe": "936200",               # Atelier Meruru DX
    "AtelierAyesha.exe": "1152300",              # Atelier Ayesha DX
    "AtelierEscha.exe": "1152310",               # Atelier Escha & Logy DX
    "AtelierShallie.exe": "1152320",             # Atelier Shallie DX
    "AtelierSophie.exe": "527270",               # Atelier Sophie
    "AtelierFiris.exe": "527290",                # Atelier Firis
    "AtelierLydie.exe": "756590",                # Atelier Lydie & Suelle
    "AtelierLulua.exe": "1045620",               # Atelier Lulua
    "AtelierRyza.exe": "1121560",                # Atelier Ryza
    "AtelierRyza2.exe": "1257290",               # Atelier Ryza 2
    "AtelierRyza3.exe": "1999770",               # Atelier Ryza 3
    "AtelierSophie2.exe": "1708610",             # Atelier Sophie 2
    "AtelierMarie.exe": "2138090",               # Atelier Marie Remake
    "AtelierResleriana.exe": "2586520",          # Atelier Resleriana
    "AtelierYumia.exe": "3123410",               # Atelier Yumia

    # -----------------------------
    # ARK / DIVERS
    # -----------------------------
    "ShooterGame.exe": "346110",                 # ARK: Survival Evolved
    "ArkAscended.exe": "2399830",                # ARK: Survival Ascended
    "ShooterGameSteam.exe": "346110",            # Alias rencontré sur certaines installations

    "DCS.exe": "223750",                              # DCS World Steam Edition

    "Popucom.exe": "2543180",                        # POPUCOM
    "Renfield.exe": "2354600",                        # Renfield: Bring Your Own Blood
    "Void Miner.exe": "3772240",                      # Void Miner – Incremental Asteroids Roguelite

    "DangerZone-Win64-Shipping.exe": "604740",       # Danger Zone
    "farm2012.exe": "273790",                         # Agricultural Simulator 2012: Deluxe Edition
    "Wreckreation.exe": "1594040",                    # Wreckreation

    "Orlando.exe": "405500",                          # Dangerous Golf
    "Orlando-Win64-Shipping.exe": "405500",          # Dangerous Golf

    "supermegabaseball.exe": "988910",               # Super Mega Baseball 3
    "cricket26.exe": "3468650",                       # Cricket 26 - The Official Game of the Ashes
    "WarAndPeace.exe": "2009780",                    # Napoleon's Eagles: Game of the Napoleonic Wars

    "VeiledExperts-Win64-Shipping_BE.exe": "1934780", # VEILED EXPERTS
    "Iridion3d.exe": "1132220",                       # Iridion 3D

    "xcom.exe": "7770",                               # X-COM: Enforcer
    "Interceptor.exe": "7730",                  # X-COM: Interceptor
    "UFO Defense_Patched.exe": "7760",               # X-COM: UFO Defense
    "runme.exe": "7650",                              # X-COM: Terror From the Deep
    "Terror From the Deep_patched.exe": "7650",      # X-COM: Terror From the Deep

    # -----------------------------
    # Assassin's Creed
    # -----------------------------
    "AssassinsCreed.exe": "15100",            # Assassin's Creed
    "AssassinsCreed_Dx9.exe": "15100",
    "AssassinsCreed_Dx10.exe": "15100",
    "AssassinsCreed2.exe": "33230",           # Assassin's Creed II
    "ACBSP.exe": "48190",                     # Assassin's Creed Brotherhood
    "ACRSP.exe": "201870",                    # Assassin's Creed Revelations
    "AC3SP.exe": "208480",                    # Assassin's Creed III
    "AC3Remastered.exe": "911400",            # Assassin's Creed III Remastered
    "AC4BFSP.exe": "242050",                  # Assassin's Creed IV Black Flag
    "AC4BFMP.exe": "242050",
    "ACRogue.exe": "311560",                  # Assassin's Creed Rogue
    "ACRogueRemastered.exe": "3316990",       # https://www.protondb.com/app/3316990
    "ACS.exe": "368500",                      # Assassin's Creed Syndicate
    "ACU.exe": "289650",                      # Assassin's Creed Unity
    "ACChroniclesChina.exe": "297110",        # Assassin's Creed Chronicles: China
    "ACChroniclesIndia.exe": "359870",        # Assassin's Creed Chronicles: India
    "ACChroniclesRussia.exe": "365590",       # Assassin's Creed Chronicles: Russia
    "ACOrigins.exe": "582160",                # Assassin's Creed Origins
    "ACOdyssey.exe": "812140",                # Assassin's Creed Odyssey
    "ACValhalla.exe": "2208920",              # Assassin's Creed Valhalla
    "ACMirage.exe": "3035570",                # Assassin's Creed Mirage
    "ACShadows.exe": "3159330",               # Assassin's Creed Shadows

    # -----------------------------
    # Batman Arkham
    # -----------------------------
    "BatmanArkhamAsylum.exe": "35140",              # Batman: Arkham Asylum GOTY
    "Batman.exe": "35140",                          # Alias Arkham Asylum
    "BatmanArkhamCity.exe": "200260",               # Batman: Arkham City GOTY
    "BatmanAC.exe": "200260",                       # Alias Arkham City
    "BatmanArkhamOrigins.exe": "209000",            # Batman: Arkham Origins
    "BatmanAO.exe": "209000",                       # Alias Arkham Origins
    "BatmanArkhamKnight.exe": "208650",             # Batman: Arkham Knight
    "BatmanAK.exe": "208650",                       # Alias Arkham Knight
    "BatmanArkhamVR.exe": "502820",                 # Batman: Arkham VR
    "BatmanArkhamShadow.exe": "2562200",            # Batman: Arkham Shadow (si version PC détectée)
    "ShippingPC-BmGame.exe": "35140",     # Arkham Asylum
    "ShippingPC-BmGame.exe": "200260",    # Arkham City (doublon impossible en dict)
    "BatmanAK-Win64-Shipping.exe": "208650",

    # -----------------------------
    # Battlefield
    # -----------------------------
    "bf3.exe": "1238820",                   # Battlefield 3
    "Battlefield3.exe": "1238820",
    "bf4.exe": "1238860",                   # Battlefield 4
    "Battlefield4.exe": "1238860",
    "bfh.exe": "1238880",                   # Battlefield Hardline
    "BattlefieldHardline.exe": "1238880",
    "bf1.exe": "1238840",                   # Battlefield 1
    "Battlefield1.exe": "1238840",
    "bfv.exe": "1238810",                   # Battlefield V
    "BattlefieldV.exe": "1238810",
    "bf2042.exe": "1517290",                # Battlefield 2042
    "Battlefield2042.exe": "1517290",

    # -----------------------------
    # Call of Duty
    # -----------------------------
    "CoD.exe": "2620",                          # Call of Duty
    "CallOfDuty.exe": "2620",
    "CoD2.exe": "2630",                         # Call of Duty 2
    "CallOfDuty2.exe": "2630",
    "CoD4MW.exe": "7940",                       # Call of Duty 4: Modern Warfare
    "iw3sp.exe": "7940",
    "iw3mp.exe": "7940",
    "CoDWaW.exe": "10090",                      # Call of Duty: World at War
    "CoD_WaW.exe": "10090",
    "iw5sp.exe": "42680",                       # Modern Warfare 2 (2009)
    "iw5mp.exe": "10190",
    "BlackOps.exe": "42700",                    # Black Ops
    "BlackOpsMP.exe": "42700",
    "iw5.exe": "42680",                         # Alias MW2
    "iw6sp.exe": "209650",                      # Modern Warfare 3 (2011)
    "iw6mp.exe": "42690",
    "BlackOps2.exe": "202970",                  # Black Ops II
    "t6sp.exe": "202970",
    "t6mp.exe": "202990",
    "Ghosts.exe": "209160",                     # Ghosts
    "iw6_ship.exe": "209160",
    "AdvancedWarfare.exe": "209660",            # Advanced Warfare
    "s1_sp64_ship.exe": "209660",
    "s1_mp64_ship.exe": "209660",
    "BlackOps3.exe": "311210",                  # Black Ops III
    "BlackOps3_UnrankedDedicatedServer.exe": "311210",
    "IW7.exe": "292730",                        # Infinite Warfare
    "iw7_ship.exe": "292730",
    "MWRemastered.exe": "393100",               # Modern Warfare Remastered
    "h1_sp64_ship.exe": "393100",
    "h1_mp64_ship.exe": "393100",
    "WWII.exe": "476600",                       # Call of Duty: WWII
    "s2_sp64_ship.exe": "476600",
    "s2_mp64_ship.exe": "476600",
    "ModernWarfare.exe": "1938090",             # Call of Duty HQ
    "cod.exe": "1938090",
    "MWII.exe": "1938090",                      # MWII (2022) via HQ
    "MWIII.exe": "1938090",                     # MWIII (2023) via HQ
    "Warzone.exe": "1938090",                   # Warzone via HQ
    "BlackOps6.exe": "2933620",                 # Black Ops 6
    # -----------------------------
    # Valve / GoldSrc
    # -----------------------------
    "hl.exe": "70",                     # Half-Life
    "cstrike.exe": "10",                # Counter-Strike
    "czero.exe": "80",                  # Counter-Strike: Condition Zero
    "gearbox.exe": "50",                # Opposing Force
    "bshift.exe": "130",                # Blue Shift
    "dmc.exe": "40",                    # Deathmatch Classic
    "ricochet.exe": "60",               # Ricochet
    "tfc.exe": "20",                    # Team Fortress Classic
    "svencoop.exe": "225840",           # Sven Co-op
    "cs2.exe": "730",
    "aperturetag.exe": "280740",
    "deadlock.exe": "1422450",
    "artifact.exe": "583950",
    "underlords.exe": "1046930",

    # -----------------------------
    # Source
    # -----------------------------
    "hl2.exe": "220",                   # Half-Life 2
    "hl2_ep1.exe": "380",               # Episode One
    "hl2_ep2.exe": "420",               # Episode Two
    "portal.exe": "400",                # Portal
    "portal2.exe": "620",               # Portal 2
    "left4dead.exe": "500",             # Left 4 Dead
    "left4dead2.exe": "550",            # Left 4 Dead 2
    "hl2mp.exe": "320",                 # HL2 Deathmatch
    "tf.exe": "440",                    # Team Fortress 2
    "dods.exe": "300",                  # Day of Defeat Source
    "csgo.exe": "730",                  # CS:GO / CS2
    "gmod.exe": "4000",                 # Garry's Mod
    "swarm.exe": "630",                 # Alien Swarm

    # -----------------------------
    # Unreal Tournament
    # -----------------------------
    "UnrealTournament.exe": "13240",
    "ut99.exe": "13240",
    "ut2004.exe": "13230",
    "ut3.exe": "13210",

    # -----------------------------
    # Unreal
    # -----------------------------
    "unreal.exe": "13250",              # Unreal Gold

    # -----------------------------
    # Quake
    # -----------------------------
    "quake.exe": "2310",
    "glquake.exe": "2310",
    "winquake.exe": "2310",
    "quake2.exe": "2320",
    "quake3.exe": "2200",
    "quake4.exe": "2210",

    # ---------------------------------
    # id Software (Doom) - Wolfenstein
    # ---------------------------------
    "doom.exe": "2280",                 # DOOM (1993)
    "doom2.exe": "2300",                # DOOM II
    "doom3.exe": "9050",
    "doom3bfg.exe": "208200",
    "DOOM64_x64.exe": "1148590",
    "DOOMTheDarkAges.exe": "3017860",

    "WolfNewOrder_x64.exe": "201810",
    "WolfOldBlood_x64.exe": "350080",

    # -----------------------------
    # GTA
    # -----------------------------
    "gta-vc.exe": "12110",              # Vice City
    "gta3.exe": "12100",                # GTA III
    "gta_sa.exe": "12120",              # San Andreas
    "GTA5.exe": "271590",
    "GTAIV.exe": "12210",
    "GTAEFLC.exe": "12220",
    "GTASA.exe": "12120",

    # -----------------------------
    # Rockstar (autres)
    # -----------------------------
    "MaxPayne.exe": "12140",
    "MaxPayne2.exe": "12150",
    "MaxPayne3.exe": "204100",                   # Max Payne 3
    "manhunt.exe": "12130",                      # Manhunt
    "mc2.exe": "12160",                           # Midnight Club II

    # -----------------------------
    # Bethesda
    # -----------------------------
    "Morrowind.exe": "22320",
    "Oblivion.exe": "22330",
    "Skyrim.exe": "72850",
    "SkyrimSE.exe": "489830",
    "SkyrimVR.exe": "611670",
    "OblivionRemastered.exe": "2623190",
    # -----------------------------
    # Resident Evil
    # -----------------------------
    "re7.exe": "418370",
    "re8.exe": "1196590",
    "RE0.exe": "339340",
    "RE1.exe": "304240",
    "RE5.exe": "21690",
    "RE6.exe": "221040",
    "rev1.exe": "287290",
    "rev2.exe": "287290",

    # -----------------------------
    # Need for Speed
    # -----------------------------
    "speed.exe": "1262540",              # Need for Speed (2015)
    "NFS16.exe": "1262540",
    "NFSPayback.exe": "1262580",         # Need for Speed Payback
    "NeedForSpeedHeat.exe": "1222680",   # Need for Speed Heat
    "NFSHeat.exe": "1222680",
    "NeedForSpeedUnbound.exe": "1846380",# Need for Speed Unbound
    "NFSUnbound.exe": "1846380",
    "nfs.exe": "17430",                  # Need for Speed Undercover
    "nfsc.exe": "8790",                  # Need for Speed Carbon
    "nfsmw.exe": "1262560",              # Need for Speed Most Wanted (2012)
    "nfsps.exe": "47870",                # Need for Speed ProStreet
    "nfss.exe": "24870",                 # Need for Speed Shift
    "shift2u.exe": "47920",              # Shift 2 Unleashed

    # -----------------------------
    # Fallout
    # -----------------------------
    "falloutw.exe": "38400",         #Fallout: A Post Nuclear Role Playing Game
    "unins000.exe": "38400",         #Fallout: A Post Nuclear Role Playing Game
    "Fallout.exe": "38400",         #Fallout: A Post Nuclear Role Playing Game
    "Fallout2.exe": "38410",        #Fallout 2: A Post Nuclear Role Playing Game
    "BOS.exe": "38420",             #Fallout Tactics: Brotherhood of Steel
    "FT Tools.exe": "38420",        #Fallout Tactics: Brotherhood of Steel
    "FalloutTactics.exe": "38420",  #Fallout Tactics: Brotherhood of Steel
    "Fallout3.exe": "22370",        #Fallout 3: Game of the Year Edition
    "FalloutLauncher.exe": "22370", #Fallout 3: Game of the Year Edition
    "FalloutNV.exe": "22380",
    "FalloutNVLauncher.exe": "22380",
    "Fallout4.exe": "377160",
    "Fallout4Launcher.exe": "377160",
    "Fallout76.exe": "1151340",
    "Project76.exe": "1151340",      # Nom interne utilisé par certaines versions
    "Fallout76Launcher.exe": "1151340",

    # -----------------------------
    # BioShock
    # -----------------------------
    "Bioshock.exe": "7670",         # BioShock
    "BioShock.exe": "7670",
    "BioshockHD.exe": "409710",          # BioShock Remastered
    "BioShockHD.exe": "409710",
    "Bioshock2.exe": "8850",        # BioShock 2
    "BioShock2.exe": "8850",
    "Bioshock2HD.exe": "409720",         # BioShock 2 Remastered
    "BioShock2HD.exe": "409720",
    "BioShockInfinite.exe": "8870",     # BioShock Infinite

    # -----------------------------
    # Deus Ex
    # -----------------------------
    "DeusEx.exe":   "6910",      # Deus Ex: Game of the Year Edition
    "DXHR.exe":     "238010",    # Deus Ex: Human Revolution - Director's Cut
    "dxhr.exe":     "28050",     # Deus Ex: Human Revolution (original)
    "DXHRDC.exe":   "238010",    # Human Revolution - Director's Cut
    "DXMD.exe":     "337000",    # Deus Ex: Mankind Divided

    # -----------------------------
    # Crysis
    # -----------------------------
    "Crysis.exe":          "17300",     # Crysis
    "Crysis64.exe":        "17300",
    "CrysisWars.exe":      "17330",     # Crysis Wars
    "Warhead.exe":         "17330",     # Crysis Warhead
    "Warhead64.exe":       "17330",
    "Crysis2.exe":         "108800",    # Crysis 2 Maximum Edition
    "Crysis2Launcher.exe": "108800",
    "Crysis3.exe":         "1282690",   # Crysis 3 Remastered
    "CrysisRemastered.exe":  "1715130", # Crysis Remastered
    "Crysis2Remastered.exe": "2096600", # Crysis 2 Remastered

    # -----------------------------
    # Euro Truck Simulator
    # -----------------------------
    "eurotrucks.exe": "232010",        # Euro Truck Simulator (2008)
    "ets.exe": "232010",               # Alias ETS1
    "eurotrucks2.exe": "227300",       # Euro Truck Simulator 2
    "eurotrucks2_linux": "227300",
    "ets2.exe": "227300",

    # -----------------------------
    # American Truck Simulator
    # -----------------------------
    "amtrucks.exe": "270880",                   # American Truck Simulator
    "amtrucks_linux": "270880",
    "ats.exe": "270880",                        # Alias ATS
    "AmericanTruckSimulator.exe": "270880",

    # -----------------------------
    # Kerbal Space Program
    # -----------------------------
    "KSP.exe": "220200",                        # Kerbal Space Program
    "KerbalSpaceProgram.exe": "220200",
    "KSP_x64.exe": "220200",
    "KSP_x64_Data.exe": "220200",

    # -----------------------------
    # Survival / Exploration
    # -----------------------------

    # No Man's Sky
    "NMS.exe": "275850",                         # No Man's Sky
    "NoMansSky.exe": "275850",

    # Subnautica
    "Subnautica.exe": "264710",                  # Subnautica
    "SubnauticaZero.exe": "848450",              # Subnautica: Below Zero
    "SubnauticaBelowZero.exe": "848450",

    # Raft
    "Raft.exe": "648800",                        # Raft
    "RaftGame.exe": "648800",

    # Grounded
    "Grounded.exe": "962130",                    # Grounded
    "maine-Win64-Shipping.exe": "962130",

    # Sons of the Forest
    "SonsOfTheForest.exe": "1326470",            # Sons of the Forest
    "SonsOfTheForest-Win64-Shipping.exe": "1326470",

    # The Forest
    "TheForest.exe": "242760",                   # The Forest
    "TheForest_x64.exe": "242760",
    "TheForest32.exe": "242760",

    # -----------------------------
    # Trails / Ys (Falcom)
    # -----------------------------

    # The Legend of Heroes: Trails
    "ed6.exe": "251150",                         # The Legend of Heroes: Trails in the Sky FC
    "ed6_win.exe": "251150",
    "ed6_2.exe": "251290",                       # Trails in the Sky SC
    "ed6_win2.exe": "251290",
    "ed6_3.exe": "445220",                       # Trails in the Sky the 3rd
    "Sen1.exe": "538680",                        # Trails of Cold Steel
    "Sen2.exe": "748490",                        # Trails of Cold Steel II
    "Sen3.exe": "991270",                        # Trails of Cold Steel III
    "Sen4.exe": "1198090",                       # Trails of Cold Steel IV
    "KuroNoKiseki.exe": "1668510",               # Trails through Daybreak
    "Kuro2.exe": "2138610",                      # Trails through Daybreak II

    # Ys
    "ys1.exe": "207350",                         # Ys I & II Chronicles+
    "ys6.exe": "207320",                         # Ys VI: The Ark of Napishtim
    "ysorigin.exe": "207230",                    # Ys Origin
    "ysf.exe": "207310",                         # Ys: The Oath in Felghana
    "ys8.exe": "579180",                         # Ys VIII: Lacrimosa of Dana
    "ys9.exe": "1351630",                        # Ys IX: Monstrum Nox
    "ysx.exe": "2731870",                        # Ys X: Nordics


    # -----------------------------
    # Naruto
    # -----------------------------
    "Naruto.exe": "234670",                      # Naruto Shippuden: Ultimate Ninja Storm
    "NSUNS.exe": "234670",
    "NSUNS2.exe": "248710",                      # Naruto Shippuden: Ultimate Ninja Storm 2
    "NSUNS3.exe": "234670",                      # Naruto Shippuden: Ultimate Ninja Storm 3 Full Burst
    "NSUNS4.exe": "349040",                      # Naruto Shippuden: Ultimate Ninja Storm 4
    "NarutoConnections.exe": "1020790",          # Naruto X Boruto Ultimate Ninja Storm Connections

    # -----------------------------
    # Dragon Ball
    # -----------------------------
    "DBXV.exe": "323470",                        # Dragon Ball Xenoverse
    "DBXV2.exe": "454650",                       # Dragon Ball Xenoverse 2
    "DBFighterZ.exe": "678950",                  # Dragon Ball FighterZ
    "DBZKakarot.exe": "851850",                  # Dragon Ball Z: Kakarot
    "DBSZ.exe": "1790600",                       # Dragon Ball: Sparking! ZERO
    # -----------------------------
    # One Piece
    # -----------------------------
    "OnePiecePirateWarriors.exe": "331600",     # One Piece Pirate Warriors 3
    "OPPW3.exe": "331600",
    "OPPW4.exe": "1172020",                      # One Piece Pirate Warriors 4
    "OnePieceWorldSeeker.exe": "755500",         # One Piece World Seeker
    "OnePieceOdyssey.exe": "814000",             # One Piece Odyssey
    # -----------------------------
    # Guilty Gear
    # -----------------------------
    "GuiltyGearXrd.exe": "376300",               # Guilty Gear Xrd -SIGN-
    "GuiltyGearXrdRE.exe": "520440",             # Guilty Gear Xrd REV 2
    "GuiltyGearStrive.exe": "1384160",           # Guilty Gear -Strive-

    # -----------------------------
    # Tekken & Mortal Kombat
    # -----------------------------
    "TekkenGame-Win64-Shipping.exe": "389730",   # Tekken 7
    "Tekken7.exe": "389730",
    "Tekken8.exe": "1778820",                    # Tekken 8
    "MKKE.exe": "237110",                        # Mortal Kombat Komplete Edition
    "MK10.exe": "307780",                        # Mortal Kombat X
    "MK11.exe": "976310",                        # Mortal Kombat 11
    "MortalKombat12.exe": "1971870",             # Mortal Kombat 1 (2023)
    "Injustice.exe": "242700",                   # Injustice: Gods Among Us
    "Injustice2.exe": "627270",                  # Injustice 2
    # -----------------------------
    # Street Fighter
    # -----------------------------
    "StreetFighterIV.exe": "45760",              # Street Fighter IV
    "SSFIV.exe": "45760",                        # Super Street Fighter IV
    "USFIV.exe": "45760",                        # Ultra Street Fighter IV
    "StreetFighterV.exe": "310950",              # Street Fighter V
    "StreetFighter6.exe": "1364780",             # Street Fighter 6
    "SF30th.exe": "586200",                      # Street Fighter 30th Anniversary Collection
    "StreetFighter30th.exe": "586200",

    # -----------------------------
    # ARMA
    # -----------------------------
    "arma3.exe": "107410",
    "arma3_x64.exe": "107410",
    # -----------------------------
    # CD Projekt RED
    # -----------------------------
    "Cyberpunk2077.exe": "1091500",
    "witcher3.exe": "292030",

    # -----------------------------
    # Rockstar
    # -----------------------------
    "RDR2.exe": "1174180",
    "RDR.exe": "2668510",                        # Red Dead Redemption
    "LANoire.exe": "110800",                     # L.A. Noire
    "Bully.exe": "12200",                        # Bully: Scholarship Edition

    # -----------------------------
    # FromSoftware
    # -----------------------------
    "eldenring.exe": "1245620",
    "start_protected_game.exe": "1245620",   # EAC launcher
    "DarkSoulsIII.exe": "374320",
    "sekiro.exe": "814380",
    "armoredcore6.exe": "1888160",

    # -----------------------------
    # Capcom
    # -----------------------------
    "MonsterHunterWilds.exe": "2246340",
    "MonsterHunterWorld.exe": "582010",
    "MonsterHunterRise.exe": "1446780",
    "RE2.exe": "883710",
    "RE3.exe": "952060",
    "re4.exe": "2050650",
    "DevilMayCry5.exe": "601150",
    "StreetFighter6.exe": "1364780",
    # -----------------------------
    # Final Fantasy
    # -----------------------------
    "ff7remake_.exe": "1462040",
    "ffxv_s.exe": "637650",
    "ffx.exe": "359870",
    "ffxiiiimg.exe": "292120",
    "ffxiii2img.exe": "292140",
    "LRFF13.exe": "345350",
    "ff7.exe": "39140",
    "ff8.exe": "39150",
    "ff9.exe": "377840",
    "ff12.exe": "595520",
    "ff14boot.exe": "39210",
    # -----------------------------
    # Persona / Atlus
    # -----------------------------
    "P5R.exe": "1687950",
    "P3R.exe": "2161700",
    "P4G.exe": "1113000",
    "SMTV.exe": "2102450",
    "Metaphor.exe": "2679460",
    # -----------------------------
    # Yakuza / Like a Dragon
    # -----------------------------
    "Yakuza0.exe": "638970",
    "YakuzaKiwami.exe": "834530",
    "YakuzaKiwami2.exe": "927380",
    "Yakuza3.exe": "1088710",
    "Yakuza4.exe": "1105500",
    "Yakuza5.exe": "1105510",
    "Yakuza6.exe": "1388590",
    "YakuzaLikeADragon.exe": "1235140",
    "LikeADragonInfiniteWealth.exe": "2072450",
    # -----------------------------
    # Dragon Age
    # -----------------------------
    "DragonAge.exe": "47810",
    "DragonAge2.exe": "1238040",
    "DragonAgeInquisition.exe": "1222690",
    "DragonAgeTheVeilguard.exe": "1845910",

    # -----------------------------
    # Bethesda
    # -----------------------------
    "Starfield.exe": "1716740",
    "DOOMx64vk.exe": "379720",          # DOOM (2016)
    "DOOMEternalx64vk.exe": "782330",

    # -----------------------------
    # Ubisoft
    # -----------------------------
    "ACValhalla.exe": "2208920",
    "ACMirage.exe": "3035570",
    "ACOdyssey.exe": "812140",
    "FarCry5.exe": "552520",
    "FarCry6.exe": "2369390",

    # -----------------------------
    # EA
    # -----------------------------
    "MassEffect.exe": "17460",
    "MassEffect2.exe": "24980",
    "MassEffect3.exe": "1238020",
    "MassEffectLauncher.exe": "1328670",
    "DeadSpaceRemake.exe": "1693980",
    "JediSurvivor.exe": "1774580",
    "JediFallenOrder.exe": "1172380",
    # -----------------------------
    # Civilization
    # -----------------------------
    "Civ4.exe": "3900",
    "Civ5.exe": "8930",
    "Civ6.exe": "289070",
    "Civ7.exe": "1295660",

    # -----------------------------
    # Paradox / Larian
    # -----------------------------
    "bg3.exe": "1086940",
    "eu4.exe": "236850",
    "ck2.exe": "203770",
    "ck3.exe": "1158310",
    "hoi4.exe": "394360",
    "stellaris.exe": "281990",
    "victoria3.exe": "529340",

    # -----------------------------
    # Total War / Guerrilla
    # -----------------------------
    "HorizonZeroDawn.exe": "1151640",
    "Rome.exe": "4760",
    "Rome2.exe": "214950",
    "Attila.exe": "325610",
    "Warhammer.exe": "364360",
    "Warhammer2.exe": "594570",
    "Warhammer3.exe": "1142710",
    "ThreeKingdoms.exe": "779340",
    "Pharaoh.exe": "1937780",

    # -----------------------------
    # Sony
    # -----------------------------
    "GoW.exe": "1593500",
    "SpiderMan.exe": "1817070",
    "SpiderMan2.exe": "2651280",
    "MilesMorales.exe": "1817190",
    "DaysGone.exe": "1259420",
    "GhostOfTsushima.exe": "2215430",
    "Returnal.exe": "1649240",


    # -----------------------------
    # Remedy
    # -----------------------------
    "AlanWake2.exe": "2841610",
    "Control.exe": "870780",

    # -----------------------------
    # Techland
    # -----------------------------
    "DyingLightGame.exe": "239140",
    "DyingLight2.exe": "534380",

    # -----------------------------
    # 4A Games
    # -----------------------------
    "MetroExodus.exe": "412020",

    # -----------------------------
    # Blizzard / Battle.net
    # -----------------------------
    "Diablo IV.exe": "2344520",          # Diablo IV Steam
    "DiabloIV.exe": "2344520",
    "Overwatch.exe": "2357570",          # Overwatch 2 Steam
    "ModernWarfare.exe": "1938090",      # Call of Duty HQ
    "cod.exe": "1938090",                # Call of Duty HQ (nouveau launcher)
    "BlackOps6.exe": "2933620",          # Black Ops 6 (via COD HQ) # Call of Duty HQ
    "MWII.exe": "1938090",               # Modern Warfare II (via COD HQ)
    "MWIII.exe": "1938090",              # Modern Warfare III (via COD HQ)
    "Warzone.exe": "1938090",            # Warzone (via COD HQ)
    "Diablo II Resurrected.exe": "2536520",     # Battle.net uniquement
    "D2R.exe": "2536520",
    # Crash Bandicoot
    "CrashBandicoot4.exe": "1378990",    # Crash Bandicoot 4: It's About Time
    # Spyro
    "Spyro-Win64-Shipping.exe": "996580",# Spyro Reignited Trilogy
    # Tony Hawk
    "THPS12.exe": "2395210",             # Tony Hawk's Pro Skater 1 + 2
    # Sekiro (Activision éditeur)
    "sekiro.exe": "814380",
    # Prototype
    "prototypef.exe": "10150",           # Prototype
    "prototype2.exe": "115320",          # Prototype 2

    # -----------------------------
    # Painkiller
    # -----------------------------
    "Painkiller.exe": "39530",                  # Painkiller Black Edition
    "PainkillerBlackEdition.exe": "39530",
    "BattleOutOfHell.exe": "39530",             # Battle Out of Hell (Black Edition)
    "PainkillerOverdose.exe": "3270",           # Painkiller: Overdose
    "PainkillerResurrection.exe": "40700",      # Painkiller: Resurrection
    "PainkillerRedemption.exe": "40710",        # Painkiller: Redemption
    "PKHD.exe": "214870",                       # Painkiller Hell & Damnation
    "PainkillerHD.exe": "214870",
    "PainkillerHellAndDamnation.exe": "214870",

    # -----------------------------
    # Killing Floor
    # -----------------------------
    "KillingFloor.exe": "1250",                 # Killing Floor
    "KF.exe": "1250",
    "KFGame.exe": "232090",                     # Killing Floor 2
    "KillingFloor2.exe": "232090",
    "KillingFloor3.exe": "1430190",             # Killing Floor 3
    "KF3.exe": "1430190",

    # -----------------------------
    # PAYDAY
    # -----------------------------
    "payday_win32_release.exe": "24240",        # PAYDAY: The Heist
    "PAYDAY.exe": "24240",
    "payday2_win32_release.exe": "218620",      # PAYDAY 2
    "payday2_release.exe": "218620",
    "PAYDAY2.exe": "218620",
    "PAYDAY3Client.exe": "1272080",             # PAYDAY 3
    "PAYDAY3.exe": "1272080",

    # -----------------------------
    # Activision
    # -----------------------------
    "cod.exe": "1938090",               # Call of Duty HQ
    # -----------------------------
    # Independant or MUlti
    # -----------------------------
    "witcher.exe": "20920",        # The Witcher Enhanced Edition
    "witcher2.exe": "20920",
    "Dishonored.exe": "205100",
    "Dishonored2.exe": "403640",
    "Prey.exe": "480490",
    "NewColossus_x64vk.exe": "612880",
    "Youngblood_x64vk.exe": "1056960",
    "Hades.exe": "1145360",
    "Hades2.exe": "1145350",
    "Factorio.exe": "427520",
    "Valheim.exe": "892970",
    "Palworld.exe": "1623730",
    "Satisfactory.exe": "526870",
    "Lethal Company.exe": "1966720",
    "ScheduleI.exe": "3164500",
    "Rust.exe": "252490",
    "DayZ_x64.exe": "221100",
    "HuntGame.exe": "594650",
    "TheFinals.exe": "2073850",
    "PUBG.exe": "578080",
    "ReadyOrNot.exe": "1144200",
    "Silkworm_patch.exe": "217200",
    "Rage.exe": "9200",
    "Rage64.exe": "9200",
    "QuakeLive.exe": "282440",
    # -----------------------------
    # Team17
    # -----------------------------
    # Worms series
    "WA.exe": "217200",                 # Worms Armageddon
    "Worms.exe": "70600",               # Worms Reloaded
    "Worms2.exe": "217120",             # Worms 2: Armageddon
    "WormsUltimateMayhem.exe": "70620", # Worms Ultimate Mayhem
    "WormsClanWars.exe": "233840",      # Worms Clan Wars
    "WormsWMD.exe": "327030",           # Worms W.M.D.
    "WormsRumble.exe": "1186040",       # Worms Rumble
    "WormsBattlegrounds.exe": "226400", # Worms Battlegrounds

    # Alien Breed series
    "AlienBreed.exe": "22610",          # Alien Breed: Impact
    "AlienBreed2.exe": "22650",         # Alien Breed 2: Assault
    "AlienBreed3.exe": "22670",         # Alien Breed 3: Descent

    # Overcooked series (Team17 publishing)
    "Overcooked.exe": "448510",         # Overcooked
    "Overcooked2.exe": "728880",        # Overcooked! 2

    # The Escapists series
    "TheEscapists.exe": "298630",       # The Escapists
    "TheEscapists2.exe": "641990",      # The Escapists 2

    # Yooka-Laylee series (Team17 publishing)
    "YookaLaylee.exe": "360830",        # Yooka-Laylee
    "YookaLaylee2.exe": "2463200",      # Yooka-Replaylee

    # Survival / simulation
    "TheSurvivalists.exe": "897450",    # The Survivalists
    "DREDGE.exe": "1562430",            # DREDGE
    "DREDGE_Blackstone.exe": "1562430",

    # Action / adventure
    "HokkoLife.exe": "824000",          # Hokko Life
    "GolfWithYourFriends.exe": "431240",# Golf With Your Friends
    "MovingOut.exe": "996770",          # Moving Out
    "MovingOut2.exe": "1641700",        # Moving Out 2

    # Simulator / strategy
    "Flockers.exe": "260330",           # Flockers
    "Sheltered.exe": "356040",          # Sheltered
    "Sheltered2.exe": "1289380",        # Sheltered 2

    # Recent Team17 titles
    "Dredge.exe": "1562430",
    "Blasphemous.exe": "774361",        # Team17 publishing
    "Thymesia.exe": "1343240",          # Team17 publishing
    # -----------------------------
    # Star WARS
    # -----------------------------

    "swep1rcr.exe": "808910",                   # STAR WARS Episode I Racer
    "starwarsracer.exe": "808910",              # STAR WARS Episode I Racer
    "swkotor.exe": "32370",                     # STAR WARS Knights of the Old Republic
    "swkotor2.exe": "208580",                   # STAR WARS Knights of the Old Republic II: The Sith Lords
    "jediacademy.exe": "6020",                  # STAR WARS Jedi Knight: Jedi Academy
    "jedioutcast.exe": "6030",                  # STAR WARS Jedi Knight II: Jedi Outcast
    "republiccommando.exe": "6000",             # STAR WARS Republic Commando
    "battlefront2classic.exe": "6060",          # STAR WARS Battlefront II (Classic, 2005)
    "starfighter.exe": "32350",                 # STAR WARS Starfighter
    "darkforces.exe": "32400",                  # STAR WARS Dark Forces (Classic, 1995)
    "clonewarsrepublicheroes.exe": "32420",     # STAR WARS The Clone Wars - Republic Heroes
    "forceunleashed.exe": "32430",              # STAR WARS The Force Unleashed Ultimate Sith Edition
    "forceunleashed2.exe": "32500",             # STAR WARS The Force Unleashed II
    "empireatwar.exe": "32470",                 # STAR WARS Empire at War Gold Pack
    "galacticbattlegrounds.exe": "356500",      # STAR WARS Galactic Battlegrounds Saga
    "legostarwars.exe": "32440",                # LEGO Star Wars: The Complete Saga
    "legostarwars_skywalker.exe": "920210",     # LEGO Star Wars: The Skywalker Saga
    "jedifallenorder.exe": "1172380",           # STAR WARS Jedi: Fallen Order
    "theoldrepublic.exe": "1286830",            # STAR WARS: The Old Republic

    # LEGO ---------------------------------------------------------------------------------
    "legoindianajones.exe": "32330",            # LEGO Indiana Jones: The Original Adventures
    "legoindy2.exe": "32450",                   # LEGO Indiana Jones 2: The Adventure Continues
    "legobatman.exe": "21000",                  # LEGO Batman: The Videogame
    "legobatman2.exe": "213330",                # LEGO Batman 2: DC Super Heroes
    "legobatman3.exe": "313690",                # LEGO Batman 3: Beyond Gotham
    "legoharrypotter.exe": "21130",             # LEGO Harry Potter: Years 1-4
    "legoharrypotter2.exe": "204120",           # LEGO Harry Potter: Years 5-7
    "legopirates.exe": "311120",                # LEGO Pirates of the Caribbean: The Video Game
    "legolotr.exe": "214510",                   # LEGO The Lord of the Rings
    "legohobbit.exe": "285160",                 # LEGO The Hobbit
    "legomarvel.exe": "249130",                 # LEGO Marvel Super Heroes
    "legomarvelavengers.exe": "405310",         # LEGO Marvel's Avengers
    "legomarvel2.exe": "647830",                # LEGO Marvel Super Heroes 2
    "legojurassicworld.exe": "352400",          # LEGO Jurassic World
    "legoworlds.exe": "332310",                 # LEGO Worlds
    "legocity.exe": "578330",                   # LEGO City Undercover
    "legoninjago.exe": "640590",                # The LEGO NINJAGO Movie Video Game
    "legoincredibles.exe": "818320",            # LEGO The Incredibles
    "legodcvillains.exe": "829110",             # LEGO DC Super-Villains
    "legomovie.exe": "267530",                  # The LEGO Movie Videogame
    "legomovie2.exe": "881320",                 # The LEGO Movie 2 Videogame
    "legobricktales.exe": "1898290",            # LEGO Bricktales
    "legobrawls.exe": "1043420",                # LEGO Brawls
    "legobuildersjourney.exe": "1544360",       # LEGO Builder's Journey
    "legostarwars3.exe": "42700",               # LEGO Star Wars III: The Clone Wars
    "legostarwarsforceawakens.exe": "438640",   # LEGO Star Wars: The Force Awakens
    # -----------------------------
    # Borderlands
    # -----------------------------
    "Borderlands.exe": "8980",                    # Borderlands GOTY
    "BorderlandsGOTY.exe": "8980",                # Borderlands GOTY
    "Borderlands2.exe": "49520",                  # Borderlands 2
    "BorderlandsPreSequel.exe": "261640",         # Borderlands: The Pre-Sequel
    "BorderlandsGOTYEnhanced.exe": "729040",      # Borderlands GOTY Enhanced
    "Borderlands3.exe": "397540",                 # Borderlands 3
    "Wonderlands.exe": "1286680",                 # Tiny Tina's Wonderlands
    "TinyTinasWonderlands.exe": "1286680",        # Tiny Tina's Wonderlands
    "NewTales.exe": "1454970",                    # New Tales from the Borderlands
    "NewTalesFromTheBorderlands.exe": "1454970",  # New Tales from the Borderlands
    "Tales.exe": "330830",                        # Tales from the Borderlands
    "TalesFromTheBorderlands.exe": "330830",      # Tales from the Borderlands
    # -----------------------------
    # Tomb Raider
    # -----------------------------
    "tombraider.exe": "224960",              # Tomb Raider I
    "tombraider2.exe": "225300",             # Tomb Raider II
    "tombraider3.exe": "225320",             # Tomb Raider III
    "tombraider4.exe": "225340",             # Tomb Raider: The Last Revelation
    "tombraider5.exe": "225360",             # Tomb Raider: Chronicles
    "tombraider6.exe": "225000",             # Tomb Raider: The Angel of Darkness
    "trl.exe": "7000",                       # Tomb Raider: Legend
    "tra.exe": "8000",                       # Tomb Raider: Anniversary
    "tru.exe": "8140",                       # Tomb Raider: Underworld
    "TombRaider.exe": "203160",              # Tomb Raider (2013)
    "ROTTR.exe": "391220",                   # Rise of the Tomb Raider
    "SOTTR.exe": "750920",                   # Shadow of the Tomb Raider
    "TombRaiderI-III.exe": "2478970",        # Tomb Raider I–III Remastered Starring Lara Croft
    "TombRaiderIV-VI.exe": "2525380",        # Tomb Raider IV–VI Remastered
    "TR2013.exe": "203160",
    "RiseoftheTombRaider.exe": "391220",
    "ShadowoftheTombRaider.exe": "750920",
    # -----------------------------
    # Hitman
    # -----------------------------
    "Hitman.exe": "6900",                     # Hitman: Codename 47
    "HitmanCodename47.exe": "6900",
    "Hitman2.exe": "6850",                    # Hitman 2: Silent Assassin
    "SilentAssassin.exe": "6850",
    "HitmanContracts.exe": "6860",            # Hitman: Contracts
    "Contracts.exe": "6860",
    "HitmanBloodMoney.exe": "6860",           # Hitman: Blood Money
    "BloodMoney.exe": "6860",
    "HMA.exe": "203140",                      # Hitman: Absolution
    "HitmanAbsolution.exe": "203140",
    "HITMAN.exe": "236870",                   # HITMAN (2016)
    "HITMAN2.exe": "863550",                  # HITMAN 2 (2018)
    "HITMAN3.exe": "1659040",                 # HITMAN World of Assassination (anciennement HITMAN 3)
    "WorldOfAssassination.exe": "1659040",
    # -----------------------------
    # Silent Hill
    # -----------------------------
    "SilentHillHomecoming.exe": "19000",      # Silent Hill: Homecoming
    "Homecoming.exe": "19000",
    "SilentHill2.exe": "2124490",             # SILENT HILL 2 (Remake)
    "SH2.exe": "2124490",
    "SilentHillf.exe": "3131230",             # SILENT HILL f
    "SHf.exe": "3131230",

    # -----------------------------
    # Metal Gear Solid
    # -----------------------------
    "mgsvtpp.exe": "287700",                    # Metal Gear Solid V: The Phantom Pain
    "mgsvm.exe": "311340",                      # Metal Gear Solid V: Ground Zeroes
    "MGS2.exe": "2131630",                      # Metal Gear Solid 2: Master Collection
    "MGS3.exe": "2131640",                      # Metal Gear Solid 3: Snake Eater Master Collection
    "MGS1.exe": "2131650",                      # Metal Gear Solid Master Collection
    "MGSCollection.exe": "2131650",

    # -----------------------------
    # Castlevania
    # -----------------------------
    "Castlevania.exe": "1018010",               # Castlevania Anniversary Collection
    "CastlevaniaAdvance.exe": "1552550",        # Castlevania Advance Collection
    "CastlevaniaDominus.exe": "2369900",        # Castlevania Dominus Collection
    "LoS.exe": "234080",                        # Castlevania: Lords of Shadow
    "LoS2.exe": "239250",                       # Castlevania: Lords of Shadow 2
    "MirrorOfFateHD.exe": "239240",             # Castlevania: Lords of Shadow - Mirror of Fate HD

    # -----------------------------
    # Sonic
    # -----------------------------
    "sonic.exe": "71340",                       # Sonic Generations
    "SonicGenerations.exe": "71340",
    "SonicMania.exe": "584400",                 # Sonic Mania
    "SonicFrontiers.exe": "1237320",            # Sonic Frontiers
    "SonicSuperstars.exe": "2022670",           # Sonic Superstars
    "SonicOrigins.exe": "1794960",              # Sonic Origins
    "SonicAdventureDX.exe": "71250",             # Sonic Adventure DX
    "SonicAdventure2.exe": "213610",             # Sonic Adventure 2
    "SonicRacing.exe": "212480",                # Sonic & All-Stars Racing Transformed
    "TeamSonicRacing.exe": "785260",            # Team Sonic Racing
    "sonic4ep1.exe": "71160",                   # Sonic the Hedgehog 4 Episode I
    "sonic4ep2.exe": "203680",                  # Sonic the Hedgehog 4 Episode II

    # -----------------------------
    # Crash Bandicoot
    # -----------------------------
    "CrashBandicoot4.exe": "1378990",            # Crash Bandicoot 4: It's About Time
    "CrashNTranced.exe": "731490",               # Crash Bandicoot N. Sane Trilogy
    "CrashBandicootNSane.exe": "731490",
    "CrashTeamRacing.exe": "731490",             # Alias N. Sane Trilogy
    "CrashTeamRacingNF.exe": "952060",           # Crash Team Racing Nitro-Fueled (si port)

    # -----------------------------
    # Spyro
    # -----------------------------
    "Spyro-Win64-Shipping.exe": "996580",        # Spyro Reignited Trilogy

    # -----------------------------
    # Rayman
    # -----------------------------
    "RaymanOrigins.exe": "207490",               # Rayman Origins
    "RaymanLegends.exe": "242550",               # Rayman Legends
    "Rayman3.exe": "270330",                     # Rayman 3 HD
    "RaymanForever.exe": "171740",               # Rayman Forever
    "Rayman2.exe": "215300",                     # Rayman 2: The Great Escape

    # -----------------------------
    # Prince of Persia
    # -----------------------------
    "PrinceOfPersia.exe": "19980",               # Prince of Persia (2008)
    "PrinceOfPersiaTheForgottenSands.exe": "33320",
    "POP2.exe": "13510",                         # Warrior Within
    "POP3.exe": "13520",                         # The Two Thrones
    "PrinceOfPersiaWW.exe": "13510",
    "PrinceOfPersiaTTT.exe": "13520",

    # -----------------------------
    # Watch Dogs
    # -----------------------------
    "WatchDogs.exe": "243470",                   # Watch Dogs
    "Watch_Dogs.exe": "243470",
    "WatchDogs2.exe": "447040",                  # Watch Dogs 2
    "Watch_Dogs_2.exe": "447040",
    "WatchDogsLegion.exe": "2231380",            # Watch Dogs: Legion
    "WatchDogsLegion_BE.exe": "2231380",

    # -----------------------------
    # The Crew
    # -----------------------------
    "TheCrew.exe": "241560",                     # The Crew
    "TheCrew2.exe": "646910",                    # The Crew 2
    "TheCrewMotorfest.exe": "2698940",            # The Crew Motorfest

    # -----------------------------
    # Borderlands
    # -----------------------------
    "Borderlands.exe": "8980",                   # Borderlands GOTY
    "BorderlandsGOTY.exe": "8980",
    "Borderlands2.exe": "49520",                 # Borderlands 2
    "BorderlandsPreSequel.exe": "261640",         # Borderlands The Pre-Sequel
    "BorderlandsGOTYEnhanced.exe": "729040",     # Borderlands GOTY Enhanced
    "Borderlands3.exe": "397540",                # Borderlands 3
    "TinyTinasWonderlands.exe": "1286680",       # Tiny Tina's Wonderlands
    "Wonderlands.exe": "1286680",
    "TalesFromTheBorderlands.exe": "330830",      # Tales from the Borderlands
    "Tales.exe": "330830",
    "NewTalesFromTheBorderlands.exe": "1454970", # New Tales from the Borderlands
    "NewTales.exe": "1454970",

    # -----------------------------
    # Metal Gear Solid (complément)
    # -----------------------------
    "MGS2Substance.exe": "2131630",              # MGS2 Master Collection
    "MGS3Subsistence.exe": "2131640",            # MGS3 Master Collection
    "mgsvtpp.exe": "287700",                     # The Phantom Pain
    "mgsvm.exe": "311340",                       # Ground Zeroes

    # -----------------------------
    # Castlevania (complément)
    # -----------------------------
    "CastlevaniaLOS.exe": "234080",              # Lords of Shadow
    "CastlevaniaLOS2.exe": "239250",             # Lords of Shadow 2

    # -----------------------------
    # Sonic (complément)
    # -----------------------------
    "SonicColors.exe": "251730",                 # Sonic Colours Ultimate
    "SonicLostWorld.exe": "263340",              # Sonic Lost World
    "SonicForces.exe": "637100",                 # Sonic Forces
    "SonicR.exe": "205950",                      # Sonic R
    "SonicCD.exe": "200940",                     # Sonic CD
    "Sonic3AIR.exe": "123456",                   # Fan project (si détecté)

    # -----------------------------
    # Crash Bandicoot (complément)
    # -----------------------------
    "Crash4.exe": "1378990",                     # Crash Bandicoot 4
    "CrashNST.exe": "731490",                    # N. Sane Trilogy
    "CTR.exe": "952060",                         # CTR Nitro Fueled (port)

    # -----------------------------
    # Spyro (complément)
    # -----------------------------
    "Spyro.exe": "996580",                       # Spyro Reignited Trilogy

    # -----------------------------
    # Rayman (complément)
    # -----------------------------
    "RaymanRavingRabbids.exe": "22230",           # Rayman Raving Rabbids
    "RaymanRavingRabbids2.exe": "34420",          # Rabbids 2
    "RaymanRavingRabbidsTV.exe": "21670",         # TV Party

    # -----------------------------
    # Prince of Persia (complément)
    # -----------------------------
    "Prince.exe": "13600",                       # Prince of Persia Classic
    "POP2008.exe": "19980",                       # Prince of Persia 2008
    "ForgottenSands.exe": "33320",                # The Forgotten Sands

    # -----------------------------
    # Watch Dogs (complément)
    # -----------------------------
    "WatchDogs.exe": "243470",
    "WatchDogs2.exe": "447040",
    "WatchDogsLegion.exe": "2231380",

    # -----------------------------
    # Far Cry complet
    # -----------------------------
    "FarCry.exe": "13520",                       # Far Cry
    "FarCry2.exe": "19900",
    "FarCry3.exe": "220240",
    "FarCry3_DX11.exe": "220240",
    "BloodDragon.exe": "233270",
    "FarCry4.exe": "298110",
    "FarCryPrimal.exe": "371660",
    "FarCry5.exe": "552520",
    "FarCryNewDawn.exe": "939960",
    "FarCry6.exe": "2369390",

    # -----------------------------
    # The Crew
    # -----------------------------
    "TheCrew.exe": "241560",
    "TheCrew2.exe": "646910",
    "TheCrewMotorfest.exe": "2698940",

    # -----------------------------
    # Borderlands (complément complet)
    # -----------------------------
    "Borderlands.exe": "8980",
    "Borderlands2.exe": "49520",
    "BorderlandsPreSequel.exe": "261640",
    "BorderlandsGOTYEnhanced.exe": "729040",
    "Borderlands3.exe": "397540",
    "TalesFromTheBorderlands.exe": "330830",
    "NewTalesFromTheBorderlands.exe": "1454970",
    "TinyTinasWonderlands.exe": "1286680",

    # -----------------------------
    # Assassin's Creed (manquants)
    # -----------------------------
    "ACLiberation.exe": "260210",                # Liberation HD
    "ACFreedomCry.exe": "271260",                # Freedom Cry
    "ACB.exe": "48190",
    "ACR.exe": "201870",

    # -----------------------------
    # Tomb Raider (complément)
    # -----------------------------
    "TombRaiderLegend.exe": "7000",
    "TombRaiderAnniversary.exe": "8000",
    "TombRaiderUnderworld.exe": "8140",

    # -----------------------------
    # Batman Arkham (complément)
    # -----------------------------
    "BatmanArkhamOriginsBlackgate.exe": "267490",

    # -----------------------------
    # Mafia
    # -----------------------------
    "Mafia.exe": "40990",
    "Mafia2.exe": "50130",
    "MafiaDefinitiveEdition.exe": "1030840",
    "MafiaIIIDefinitiveEdition.exe": "360430",

    # -----------------------------
    # Saints Row
    # -----------------------------
    "SaintsRow2.exe": "9480",
    "SaintsRowTheThird.exe": "55230",
    "SaintsRowIV.exe": "206420",
    "SaintsRow2022.exe": "742420",

    # -----------------------------
    # Dead Space
    # -----------------------------
    "DeadSpace.exe": "17470",
    "DeadSpace2.exe": "47780",
    "DeadSpace3.exe": "1238060",
    "DeadSpaceRemake.exe": "1693980",

    # -----------------------------
    # Darksiders
    # -----------------------------
    "Darksiders.exe": "50620",
    "Darksiders2.exe": "50650",
    "Darksiders3.exe": "606280",
    "DarksidersGenesis.exe": "710920",

    # -----------------------------
    # Prince-like Action Adventure
    # -----------------------------
    "BeyondGoodAndEvil.exe": "15130",
    "BeyondGoodAndEvil2.exe": "25500",

    # -----------------------------
    # Jak / Ratchet / Platformers
    # -----------------------------
    "RatchetClankRiftApart.exe": "1895880",

    # -----------------------------
    # Mega Man
    # -----------------------------
    "MegaManLegacy.exe": "363440",
    "MegaManXLegacy.exe": "364680",
    "MegaMan11.exe": "742300",

    # -----------------------------
    # Resident Evil (complément)
    # -----------------------------
    "bio4.exe": "254700",                       # Resident Evil 4 Classic
    "re5dx9.exe": "21690",
    "re6.exe": "221040",

    # -----------------------------
    # Kingdom Hearts
    # -----------------------------
    "KingdomHearts1.exe": "2552430",
    "KingdomHearts2.exe": "2552440",

    # -----------------------------
    # Halo
    # -----------------------------
    "MCC-Win64-Shipping.exe": "976730",

    # -----------------------------
    # Gears of War
    # -----------------------------
    "GearsTactics.exe": "1184050",

    # -----------------------------
    # Forza
    # -----------------------------
    "ForzaHorizon4.exe": "1293830",
    "ForzaHorizon5.exe": "1551360",
    "ForzaMotorsport.exe": "2440510",

    # -----------------------------
    # Doom / Quake / id (complément)
    # -----------------------------
    "DOOMx64.exe": "379720",
    "DOOMEternalx64vk.exe": "782330",
    "QuakeLive.exe": "282440",

    # -----------------------------
    # Portal / Valve (complément)
    # -----------------------------
    "portal2_linux.exe": "620",
    "left4dead2.exe": "550",

    # -----------------------------
    # Ori
    # -----------------------------
    "Ori.exe": "261570",
    "Ori2.exe": "1057090",

    # -----------------------------
    # Hollow Knight / Metroidvania
    # -----------------------------
    "HollowKnight.exe": "367520",
    "Blasphemous.exe": "774361",

    # -----------------------------
    # Nier
    # -----------------------------
    "NierAutomata.exe": "524220",
    "NierReplicant.exe": "1113560",

    # -----------------------------
    # Persona / SMT (complément)
    # -----------------------------
    "Persona5.exe": "1687950",
    "Persona3Reload.exe": "2161700",

    # -----------------------------
    # Like a Dragon (complément)
    # -----------------------------
    "Yakuza7.exe": "1235140",
    "Judgment.exe": "2058180",
    "LostJudgment.exe": "2058190",
}
