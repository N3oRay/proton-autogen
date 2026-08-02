# -----------------------------------------------------------------
# AppIDs connus pour des exécutables spécifiques, utilisés en dernier
# recours quand aucune détection automatique (env, appmanifest,
# steam_appid.txt) n'a abouti. Utile pour les jeux anciens copiés
# hors de leur bibliothèque Steam d'origine (GOG, backups, etc.).
# Clé : nom de fichier de l'exécutable (insensible à la casse).
# -----------------------------------------------------------------
KNOWN_APPIDS = {
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

    # -----------------------------
    # id Software (Doom)
    # -----------------------------
    "doom.exe": "2280",                 # DOOM (1993)
    "doom2.exe": "2300",                # DOOM II
    "doom3.exe": "9050",
    "doom3bfg.exe": "208200",

    # -----------------------------
    # GTA
    # -----------------------------
    "gta-vc.exe": "12110",              # Vice City
    "gta3.exe": "12100",                # GTA III
    "gta_sa.exe": "12120",              # San Andreas
    "GTA5.exe": "271590",

    # -----------------------------
    # Rockstar (autres)
    # -----------------------------
    "MaxPayne.exe": "12140",
    "MaxPayne2.exe": "12150",

    # -----------------------------
    # Bethesda
    # -----------------------------
    "Morrowind.exe": "22320",
    "Oblivion.exe": "22330",
    "Skyrim.exe": "72850",
    "SkyrimSE.exe": "489830",

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
    "Fallout3.exe": "22370",
    "FalloutNV.exe": "22380",
    "Fallout4.exe": "377160",

    # -----------------------------
    # BioShock
    # -----------------------------
    "Bioshock.exe": "7670",
    "Bioshock2.exe": "8850",

    # -----------------------------
    # Deus Ex
    # -----------------------------
    "DeusEx.exe": "6910",
    "DXHR.exe": "238010",               # Human Revolution

    # -----------------------------
    # Crysis
    # -----------------------------
    "Crysis.exe": "17300",
    "Crysis64.exe": "17300",

    # -----------------------------
    # Far Cry
    # -----------------------------
    "FarCry.exe": "13520",

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
    "MonsterHunterWorld.exe": "582010",
    "MonsterHunterRise.exe": "1446780",
    "RE2.exe": "883710",
    "RE3.exe": "952060",
    "re4.exe": "2050650",
    "DevilMayCry5.exe": "601150",
    "StreetFighter6.exe": "1364780",

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
    "MassEffectLauncher.exe": "1328670",
    "DeadSpace.exe": "1693980",
    "JediSurvivor.exe": "1774580",
    "JediFallenOrder.exe": "1172380",

    # -----------------------------
    # Larian
    # -----------------------------
    "bg3.exe": "1086940",

    # -----------------------------
    # Guerrilla
    # -----------------------------
    "HorizonZeroDawn.exe": "1151640",

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
    "Helldivers2.exe": "553850",

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
    "Overwatch.exe": "2357570",          # Overwatch 2 Steam
    "ModernWarfare.exe": "1938090",      # Call of Duty HQ / MWIII
    "DiabloIV.exe": "2344520",

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
}
