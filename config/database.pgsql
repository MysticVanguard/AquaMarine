CREATE TABLE IF NOT EXISTS guild_settings(
    guild_id BIGINT PRIMARY KEY,
    prefix TEXT
);


CREATE TABLE IF NOT EXISTS user_settings(
    user_id BIGINT PRIMARY KEY
);


CREATE TABLE IF NOT EXISTS role_list(
    guild_id BIGINT,
    role_id BIGINT,
    key TEXT,
    value TEXT,
    PRIMARY KEY (guild_id, role_id, key)
);


CREATE TABLE IF NOT EXISTS channel_list(
    guild_id BIGINT,
    channel_id BIGINT,
    key TEXT,
    value TEXT,
    PRIMARY KEY (guild_id, channel_id, key)
);

CREATE TABLE IF NOT EXISTS user_balance (
    user_id BIGINT,
    balance INTEGER NOT NULL DEFAULT 0,
    doubloon INTEGER NOT NULL DEFAULT 0,
    casts INTEGER NOT NULL DEFAULT 0,
    extra_points INT NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS user_fish_inventory (
    user_id BIGINT,
    fish TEXT,
    fish_name TEXT,
    tank_fish TEXT NOT NULL DEFAULT '',
    fish_level INT NOT NULL DEFAULT 1,
    fish_xp INT NOT NULL DEFAULT 0,
    fish_xp_max INT NOT NULL DEFAULT 25,
    fish_size TEXT,
    fish_remove_time TIMESTAMP,
    fish_entertain_time TIMESTAMP,
    fish_feed_time TIMESTAMP,
    fish_alive BOOLEAN DEFAULT TRUE,
    death_time TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_item_inventory (
    user_id BIGINT,
    cfb INT NOT NULL DEFAULT 0,
    ufb INT NOT NULL DEFAULT 0,
    rfb INT NOT NULL DEFAULT 0,
    ifb INT NOT NULL DEFAULT 0,
    hlfb INT NOT NULL DEFAULT 0,
    flakes INT NOT NULL DEFAULT 0,
    revival INT NOT NULL DEFAULT 0,
    pellets INT NOT NULL DEFAULT 0,
    wafers INT NOT NULL DEFAULT 0,
    experience_potions INT NOT NULL DEFAULT 0,
    mutation_potions INT NOT NULL DEFAULT 0,
    feeding_potions INT NOT NULL DEFAULT 0,
    pile_of_bottle_caps INT NOT NULL DEFAULT 0,
    plastic_bottle INT NOT NULL DEFAULT 0,
    plastic_bag INT NOT NULL DEFAULT 0,
    seaweed_scraps INT NOT NULL DEFAULT 0,
    broken_fishing_net INT NOT NULL DEFAULT 0,
    halfeaten_flip_flop INT NOT NULL DEFAULT 0,
    pile_of_straws INT NOT NULL DEFAULT 0,
    old_boot INT NOT NULL DEFAULT 0,
    old_tire INT NOT NULL DEFAULT 0,
    fishing_boots INT NOT NULL DEFAULT 0,
    trash_toys INT NOT NULL DEFAULT 0,
    new_location_unlock INT NOT NULL DEFAULT 0,
    super_food INT NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id)
);



CREATE TABLE IF NOT EXISTS user_tank_inventory (
    user_id BIGINT,
    tank BOOLEAN[] NOT NULL DEFAULT '{FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE}',
    tank_type TEXT[] NOT NULL DEFAULT '{"", "", "", "", "", "", "", "", "", ""}',
    tank_name TEXT[] NOT NULL DEFAULT '{"", "", "", "", "", "", "", "", "", ""}',
    fish_room INT[] NOT NULL DEFAULT '{0, 0, 0, 0, 0, 0, 0, 0, 0, 0}',
    xl_fish_room INT[] NOT NULL DEFAULT '{0, 0, 0, 0, 0, 0, 0, 0, 0, 0}',
    tiny_fish_room INT[] NOT NULL DEFAULT '{0, 0, 0, 0, 0, 0, 0, 0, 0, 0}',
    tank_theme TEXT[] NOT NULL DEFAULT '{"", "", "", "", "", "", "", "", "", ""}',
    tank_clean_time TIMESTAMP[] NOT NULL DEFAULT '{NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL}',
    tank_entertain_time TIMESTAMP[] NOT NULL DEFAULT '{NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL}',
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS user_upgrades (
    user_id BIGINT,
    rod_upgrade INT NOT NULL DEFAULT 0,
    bait_upgrade INT NOT NULL DEFAULT 0,
    line_upgrade INT NOT NULL DEFAULT 0,
    lure_upgrade INT NOT NULL DEFAULT 0,
    crate_chance_upgrade INT NOT NULL DEFAULT 0,
    weight_upgrade INT NOT NULL DEFAULT 0,
    crate_tier_upgrade INT NOT NULL DEFAULT 0,
    bleach_upgrade INT NOT NULL DEFAULT 0,
    toys_upgrade INT NOT NULL DEFAULT 0,
    amazement_upgrade INT NOT NULL DEFAULT 0,
    mutation_upgrade INT NOT NULL DEFAULT 0,
    big_servings_upgrade INT NOT NULL DEFAULT 0,
    hygienic_upgrade INT NOT NULL DEFAULT 0,
    feeding_upgrade INT NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS user_achievements_milestones (
    user_id BIGINT,
    times_entertained_milestone INT NOT NULL DEFAULT 96,
    times_fed_milestone INT NOT NULL DEFAULT 1,
    times_cleaned_milestone INT NOT NULL DEFAULT 12,
    times_caught_milestone INT NOT NULL DEFAULT 24,
    times_gambled_milestone INT NOT NULL DEFAULT 5,
    money_gained_milestone INT NOT NULL DEFAULT 1000,
    tanks_owned_milestone INT NOT NULL DEFAULT 1,
    times_entertained_milestone_done BOOLEAN NOT NULL DEFAULT FALSE,
    times_fed_milestone_done BOOLEAN NOT NULL DEFAULT FALSE,
    times_cleaned_milestone_done BOOLEAN NOT NULL DEFAULT FALSE,
    times_caught_milestone_done BOOLEAN NOT NULL DEFAULT FALSE,
    times_gambled_milestone_done BOOLEAN NOT NULL DEFAULT FALSE,
    money_gained_milestone_done BOOLEAN NOT NULL DEFAULT FALSE,
    tanks_owned_milestone_done BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS user_achievements (
    user_id BIGINT,
    times_entertained INT NOT NULL DEFAULT 0,
    times_fed INT NOT NULL DEFAULT 0,
    times_cleaned INT NOT NULL DEFAULT 0,
    times_caught INT NOT NULL DEFAULT 0,
    times_gambled INT NOT NULL DEFAULT 0,
    money_gained INT NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS command_counter(
    command_name TEXT PRIMARY KEY,
    count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fish_pool_location(
    banggai_cardinalfish_count INT NOT NULL DEFAULT 100,
    black_orchid_betta_count INT NOT NULL DEFAULT 100,
    blue_diamond_discus_count INT NOT NULL DEFAULT 100,
    bluefin_notho_count INT NOT NULL DEFAULT 100,
    caribbean_hermit_crab_count INT NOT NULL DEFAULT 100,
    clownfish_count INT NOT NULL DEFAULT 100,
    electric_yellow_lab_count INT NOT NULL DEFAULT 100,
    gold_doubloon_molly_count INT NOT NULL DEFAULT 100,
    goldfish_count INT NOT NULL DEFAULT 100,
    guppies_count INT NOT NULL DEFAULT 100,
    harlequin_filefish_count INT NOT NULL DEFAULT 100,
    harlequin_rasboras_count INT NOT NULL DEFAULT 100,
    headshield_slug_count INT NOT NULL DEFAULT 100,
    moliro_tropheus_count INT NOT NULL DEFAULT 100,
    neon_tetra_school_count INT NOT NULL DEFAULT 100,
    paradise_fish_count INT NOT NULL DEFAULT 100,
    pea_puffer_school_count INT NOT NULL DEFAULT 100,
    phantom_tetra_school_count INT NOT NULL DEFAULT 100,
    pineapple_betta_count INT NOT NULL DEFAULT 100,
    rainbow_kribensis_cichlid_count INT NOT NULL DEFAULT 100,
    red_betta_count INT NOT NULL DEFAULT 100,
    red_claw_crab_count INT NOT NULL DEFAULT 100,
    royal_blue_betta_count INT NOT NULL DEFAULT 100,
    sea_goldie_count INT NOT NULL DEFAULT 100,
    shrimp_count INT NOT NULL DEFAULT 100,
    swordtail_fish_count INT NOT NULL DEFAULT 100,
    tiger_barb_count INT NOT NULL DEFAULT 100,
    turquoise_blue_betta_count INT NOT NULL DEFAULT 100,
    zebra_danios_count INT NOT NULL DEFAULT 100,
    american_lobster_count INT NOT NULL DEFAULT 100,
    angelfish_count INT NOT NULL DEFAULT 100,
    black_crappie_count INT NOT NULL DEFAULT 100,
    blue_maomao_count INT NOT NULL DEFAULT 100,
    bluegill_count INT NOT NULL DEFAULT 100,
    bottlenose_dolphin_count INT NOT NULL DEFAULT 100,
    brook_trout_count INT NOT NULL DEFAULT 100,
    brown_trout_count INT NOT NULL DEFAULT 100,
    cowfish_count INT NOT NULL DEFAULT 100,
    electric_blue_hap_count INT NOT NULL DEFAULT 100,
    giant_sea_bass_count INT NOT NULL DEFAULT 100,
    koi_count INT NOT NULL DEFAULT 100,
    largemouth_bass_count INT NOT NULL DEFAULT 100,
    northern_hogsucker_count INT NOT NULL DEFAULT 100,
    ocean_sunfish_count INT NOT NULL DEFAULT 100,
    oscar_cichlid_count INT NOT NULL DEFAULT 100,
    pufferfish_count INT NOT NULL DEFAULT 100,
    pumpkinseed_count INT NOT NULL DEFAULT 100,
    raccoon_butterflyfish_count INT NOT NULL DEFAULT 100,
    rainbow_trout_count INT NOT NULL DEFAULT 100,
    red_snapper_count INT NOT NULL DEFAULT 100,
    redbellied_piranha_count INT NOT NULL DEFAULT 100,
    regal_blue_tang_count INT NOT NULL DEFAULT 100,
    seahorse_count INT NOT NULL DEFAULT 100,
    squid_count INT NOT NULL DEFAULT 100,
    starfish_count INT NOT NULL DEFAULT 100,
    yellow_perch_count INT NOT NULL DEFAULT 100,
    yellow_tang_count INT NOT NULL DEFAULT 100,
    carp_count INT NOT NULL DEFAULT 100,
    catfish_count INT NOT NULL DEFAULT 100,
    clown_triggerfish_count INT NOT NULL DEFAULT 100,
    striped_marlin_count INT NOT NULL DEFAULT 100,
    tuna_count INT NOT NULL DEFAULT 100,
    acorn_goldfish_count INT NOT NULL DEFAULT 25,
    boesemani_rainbowfish_count INT NOT NULL DEFAULT 25,
    fishra_count INT NOT NULL DEFAULT 25,
    santa_goldfish_count INT NOT NULL DEFAULT 25,
    beefish_count INT NOT NULL DEFAULT 25,
    cotton_candy_lobster_count INT NOT NULL DEFAULT 25,
    dracofish_count INT NOT NULL DEFAULT 25,
    ghigeon_count INT NOT NULL DEFAULT 25,
    gingerbread_axolotl_count INT NOT NULL DEFAULT 25,
    taste_of_the_rainbow_count INT NOT NULL DEFAULT 25,
    asian_arowana_count INT NOT NULL DEFAULT 25,
    kraken_count INT NOT NULL DEFAULT 25,
    sockeye_salmon_count INT NOT NULL DEFAULT 25,
    anglerfish_count INT NOT NULL DEFAULT 50,
    ifish_count INT NOT NULL DEFAULT 15,
    mahi_mahi_count INT NOT NULL DEFAULT 15,
    pifish_count INT NOT NULL DEFAULT 15,
    omnifish_count INT NOT NULL DEFAULT 5,
    bobtail_squid_count INT NOT NULL DEFAULT 50,
    christmastreefish_count INT NOT NULL DEFAULT 50,
    scaly_foot_snail_count INT NOT NULL DEFAULT 50,
    western_box_turtle_count INT NOT NULL DEFAULT 50,
    atlantic_sturgeon_count INT NOT NULL DEFAULT 50,
    axolotl_count INT NOT NULL DEFAULT 50,
    blobfish_count INT NOT NULL DEFAULT 50,
    cuttlefish_count INT NOT NULL DEFAULT 50,
    mantis_shrimp_count INT NOT NULL DEFAULT 50,
    moon_jellyfish_count INT NOT NULL DEFAULT 50,
    paddlefish_count INT NOT NULL DEFAULT 50,
    palomino_trout_count INT NOT NULL DEFAULT 50,
    quillback_count INT NOT NULL DEFAULT 50,
    school_of_betta_count INT NOT NULL DEFAULT 50,
    starfish_with_pants_count INT NOT NULL DEFAULT 50,
    wild_axolotl_count INT NOT NULL DEFAULT 50,
    codefish_count INT NOT NULL DEFAULT 50,
    coelacanth_count INT NOT NULL DEFAULT 50,
    longnose_gar_count INT NOT NULL DEFAULT 50,
    spotted_gar_count INT NOT NULL DEFAULT 50,
    great_crested_newt_count INT NOT NULL DEFAULT 75,
    moorii_ikola_tropheus_count INT NOT NULL DEFAULT 75,
    panda_telescope_goldfish_count INT NOT NULL DEFAULT 75,
    red_handfish_count INT NOT NULL DEFAULT 75,
    sea_bunny_count INT NOT NULL DEFAULT 75,
    turkeyfish_count INT NOT NULL DEFAULT 75,
    white_red_cap_goldfish_count INT NOT NULL DEFAULT 75,
    black_drakefish_count INT NOT NULL DEFAULT 75,
    chickfish_school_count INT NOT NULL DEFAULT 75,
    coconut_crab_count INT NOT NULL DEFAULT 75,
    cornucopish_count INT NOT NULL DEFAULT 75,
    dumbo_octopus_count INT NOT NULL DEFAULT 75,
    firefly_axolotl_count INT NOT NULL DEFAULT 75,
    flowerhorn_cichlid_count INT NOT NULL DEFAULT 75,
    green_drakefish_count INT NOT NULL DEFAULT 75,
    lionfish_count INT NOT NULL DEFAULT 75,
    manatee_count INT NOT NULL DEFAULT 75,
    mandarinfish_count INT NOT NULL DEFAULT 75,
    narwhal_count INT NOT NULL DEFAULT 75,
    quoyi_parrotfish_count INT NOT NULL DEFAULT 75,
    red_drakefish_count INT NOT NULL DEFAULT 75,
    seal_count INT NOT NULL DEFAULT 75,
    surge_wrasse_count INT NOT NULL DEFAULT 75,
    victory_drakefish_count INT NOT NULL DEFAULT 75,
    walking_batfish_count INT NOT NULL DEFAULT 75,
    bowfin_count INT NOT NULL DEFAULT 75,
    great_white_shark_count INT NOT NULL DEFAULT 75,
    manta_ray_count INT NOT NULL DEFAULT 75,
    muskellunge_count INT NOT NULL DEFAULT 75,
    orca_count INT NOT NULL DEFAULT 75,
    redtail_catfish_count INT NOT NULL DEFAULT 75,
    smalltooth_sawfish_count INT NOT NULL DEFAULT 75,
    walleye_count INT NOT NULL DEFAULT 75,
    whale_shark_count INT NOT NULL DEFAULT 75,
    bluntnose_minnows_count INT NOT NULL DEFAULT 100,
    congo_tetra_school_count INT NOT NULL DEFAULT 75,
    crawfish_count INT NOT NULL DEFAULT 75,
    yellow_goby_school_count INT NOT NULL DEFAULT 75,
    current_darter_school_count INT NOT NULL DEFAULT 50,
    blue_goby_school_count INT NOT NULL DEFAULT 50,
    atlantic_needlefish_count INT NOT NULL DEFAULT 50,
    black_sea_bass_count INT NOT NULL DEFAULT 25,
    red_rainbowfish_count INT NOT NULL DEFAULT 75,
    turquoise_rainbowfish_count INT NOT NULL DEFAULT 50,
    blue_catfish_count INT NOT NULL DEFAULT 75,
    belted_crawfish_count INT NOT NULL DEFAULT 75,
    river_lamprey_count INT NOT NULL DEFAULT 50,
    pink_river_dolphin_count INT NOT NULL DEFAULT 25,
    goonch_catfish_count INT NOT NULL DEFAULT 15,
    school_of_sardines_count INT NOT NULL DEFAULT 50,
    crown_jellyfish_count INT NOT NULL DEFAULT 100,
    lanternfish_count INT NOT NULL DEFAULT 100,
    barreleye_count INT NOT NULL DEFAULT 75,
    gulper_eel_count INT NOT NULL DEFAULT 50,
    glass_octopus_count INT NOT NULL DEFAULT 50,
    galaxyfish_count INT NOT NULL DEFAULT 15,
    percula_clownfish_count INT NOT NULL DEFAULT 100,
    firefish_goby_school_count INT NOT NULL DEFAULT 100,
    royal_gramma_count INT NOT NULL DEFAULT 100,
    yellow_boxfish_count INT NOT NULL DEFAULT 50,
    longspine_porcupinefish_count INT NOT NULL DEFAULT 50,
    yellow_banded_possum_wrasse_count INT NOT NULL DEFAULT 50,
    bartlett_anthia_count INT NOT NULL DEFAULT 25
);

CREATE TABLE IF NOT EXISTS user_location_info(
    user_id BIGINT,
    current_location TEXT NOT NULL DEFAULT '',
    banggai_cardinalfish_caught INT NOT NULL DEFAULT 0,
    black_orchid_betta_caught INT NOT NULL DEFAULT 0,
    blue_diamond_discus_caught INT NOT NULL DEFAULT 0,
    bluefin_notho_caught INT NOT NULL DEFAULT 0,
    caribbean_hermit_crab_caught INT NOT NULL DEFAULT 0,
    clownfish_caught INT NOT NULL DEFAULT 0,
    electric_yellow_lab_caught INT NOT NULL DEFAULT 0,
    gold_doubloon_molly_caught INT NOT NULL DEFAULT 0,
    goldfish_caught INT NOT NULL DEFAULT 0,
    guppies_caught INT NOT NULL DEFAULT 0,
    harlequin_filefish_caught INT NOT NULL DEFAULT 0,
    harlequin_rasboras_caught INT NOT NULL DEFAULT 0,
    headshield_slug_caught INT NOT NULL DEFAULT 0,
    moliro_tropheus_caught INT NOT NULL DEFAULT 0,
    neon_tetra_school_caught INT NOT NULL DEFAULT 0,
    paradise_fish_caught INT NOT NULL DEFAULT 0,
    pea_puffer_school_caught INT NOT NULL DEFAULT 0,
    phantom_tetra_school_caught INT NOT NULL DEFAULT 0,
    pineapple_betta_caught INT NOT NULL DEFAULT 0,
    rainbow_kribensis_cichlid_caught INT NOT NULL DEFAULT 0,
    red_betta_caught INT NOT NULL DEFAULT 0,
    red_claw_crab_caught INT NOT NULL DEFAULT 0,
    royal_blue_betta_caught INT NOT NULL DEFAULT 0,
    sea_goldie_caught INT NOT NULL DEFAULT 0,
    shrimp_caught INT NOT NULL DEFAULT 0,
    swordtail_fish_caught INT NOT NULL DEFAULT 0,
    tiger_barb_caught INT NOT NULL DEFAULT 0,
    turquoise_blue_betta_caught INT NOT NULL DEFAULT 0,
    zebra_danios_caught INT NOT NULL DEFAULT 0,
    american_lobster_caught INT NOT NULL DEFAULT 0,
    angelfish_caught INT NOT NULL DEFAULT 0,
    black_crappie_caught INT NOT NULL DEFAULT 0,
    blue_maomao_caught INT NOT NULL DEFAULT 0,
    bluegill_caught INT NOT NULL DEFAULT 0,
    bottlenose_dolphin_caught INT NOT NULL DEFAULT 0,
    brook_trout_caught INT NOT NULL DEFAULT 0,
    brown_trout_caught INT NOT NULL DEFAULT 0,
    cowfish_caught INT NOT NULL DEFAULT 0,
    electric_blue_hap_caught INT NOT NULL DEFAULT 0,
    giant_sea_bass_caught INT NOT NULL DEFAULT 0,
    koi_caught INT NOT NULL DEFAULT 0,
    largemouth_bass_caught INT NOT NULL DEFAULT 0,
    northern_hogsucker_caught INT NOT NULL DEFAULT 0,
    ocean_sunfish_caught INT NOT NULL DEFAULT 0,
    oscar_cichlid_caught INT NOT NULL DEFAULT 0,
    pufferfish_caught INT NOT NULL DEFAULT 0,
    pumpkinseed_caught INT NOT NULL DEFAULT 0,
    raccoon_butterflyfish_caught INT NOT NULL DEFAULT 0,
    rainbow_trout_caught INT NOT NULL DEFAULT 0,
    red_snapper_caught INT NOT NULL DEFAULT 0,
    redbellied_piranha_caught INT NOT NULL DEFAULT 0,
    regal_blue_tang_caught INT NOT NULL DEFAULT 0,
    seahorse_caught INT NOT NULL DEFAULT 0,
    squid_caught INT NOT NULL DEFAULT 0,
    starfish_caught INT NOT NULL DEFAULT 0,
    yellow_perch_caught INT NOT NULL DEFAULT 0,
    yellow_tang_caught INT NOT NULL DEFAULT 0,
    carp_caught INT NOT NULL DEFAULT 0,
    catfish_caught INT NOT NULL DEFAULT 0,
    clown_triggerfish_caught INT NOT NULL DEFAULT 0,
    striped_marlin_caught INT NOT NULL DEFAULT 0,
    tuna_caught INT NOT NULL DEFAULT 0,
    acorn_goldfish_caught INT NOT NULL DEFAULT 0,
    boesemani_rainbowfish_caught INT NOT NULL DEFAULT 0,
    fishra_caught INT NOT NULL DEFAULT 0,
    santa_goldfish_caught INT NOT NULL DEFAULT 0,
    beefish_caught INT NOT NULL DEFAULT 0,
    cotton_candy_lobster_caught INT NOT NULL DEFAULT 0,
    dracofish_caught INT NOT NULL DEFAULT 0,
    ghigeon_caught INT NOT NULL DEFAULT 0,
    gingerbread_axolotl_caught INT NOT NULL DEFAULT 0,
    taste_of_the_rainbow_caught INT NOT NULL DEFAULT 0,
    asian_arowana_caught INT NOT NULL DEFAULT 0,
    kraken_caught INT NOT NULL DEFAULT 0,
    sockeye_salmon_caught INT NOT NULL DEFAULT 0,
    anglerfish_caught INT NOT NULL DEFAULT 0,
    ifish_caught INT NOT NULL DEFAULT 0,
    mahi_mahi_caught INT NOT NULL DEFAULT 0,
    pifish_caught INT NOT NULL DEFAULT 0,
    omnifish_caught INT NOT NULL DEFAULT 0,
    bobtail_squid_caught INT NOT NULL DEFAULT 0,
    christmastreefish_caught INT NOT NULL DEFAULT 0,
    scaly_foot_snail_caught INT NOT NULL DEFAULT 0,
    western_box_turtle_caught INT NOT NULL DEFAULT 0,
    atlantic_sturgeon_caught INT NOT NULL DEFAULT 0,
    axolotl_caught INT NOT NULL DEFAULT 0,
    blobfish_caught INT NOT NULL DEFAULT 0,
    cuttlefish_caught INT NOT NULL DEFAULT 0,
    mantis_shrimp_caught INT NOT NULL DEFAULT 0,
    moon_jellyfish_caught INT NOT NULL DEFAULT 0,
    paddlefish_caught INT NOT NULL DEFAULT 0,
    palomino_trout_caught INT NOT NULL DEFAULT 0,
    quillback_caught INT NOT NULL DEFAULT 0,
    school_of_betta_caught INT NOT NULL DEFAULT 0,
    starfish_with_pants_caught INT NOT NULL DEFAULT 0,
    wild_axolotl_caught INT NOT NULL DEFAULT 0,
    codefish_caught INT NOT NULL DEFAULT 0,
    coelacanth_caught INT NOT NULL DEFAULT 0,
    longnose_gar_caught INT NOT NULL DEFAULT 0,
    spotted_gar_caught INT NOT NULL DEFAULT 0,
    great_crested_newt_caught INT NOT NULL DEFAULT 0,
    moorii_ikola_tropheus_caught INT NOT NULL DEFAULT 0,
    panda_telescope_goldfish_caught INT NOT NULL DEFAULT 0,
    red_handfish_caught INT NOT NULL DEFAULT 0,
    sea_bunny_caught INT NOT NULL DEFAULT 0,
    turkeyfish_caught INT NOT NULL DEFAULT 0,
    white_red_cap_goldfish_caught INT NOT NULL DEFAULT 0,
    black_drakefish_caught INT NOT NULL DEFAULT 0,
    chickfish_school_caught INT NOT NULL DEFAULT 0,
    coconut_crab_caught INT NOT NULL DEFAULT 0,
    cornucopish_caught INT NOT NULL DEFAULT 0,
    dumbo_octopus_caught INT NOT NULL DEFAULT 0,
    firefly_axolotl_caught INT NOT NULL DEFAULT 0,
    flowerhorn_cichlid_caught INT NOT NULL DEFAULT 0,
    green_drakefish_caught INT NOT NULL DEFAULT 0,
    lionfish_caught INT NOT NULL DEFAULT 0,
    manatee_caught INT NOT NULL DEFAULT 0,
    mandarinfish_caught INT NOT NULL DEFAULT 0,
    narwhal_caught INT NOT NULL DEFAULT 0,
    quoyi_parrotfish_caught INT NOT NULL DEFAULT 0,
    red_drakefish_caught INT NOT NULL DEFAULT 0,
    seal_caught INT NOT NULL DEFAULT 0,
    surge_wrasse_caught INT NOT NULL DEFAULT 0,
    victory_drakefish_caught INT NOT NULL DEFAULT 0,
    walking_batfish_caught INT NOT NULL DEFAULT 0,
    bowfin_caught INT NOT NULL DEFAULT 0,
    great_white_shark_caught INT NOT NULL DEFAULT 0,
    manta_ray_caught INT NOT NULL DEFAULT 0,
    muskellunge_caught INT NOT NULL DEFAULT 0,
    orca_caught INT NOT NULL DEFAULT 0,
    redtail_catfish_caught INT NOT NULL DEFAULT 0,
    smalltooth_sawfish_caught INT NOT NULL DEFAULT 0,
    walleye_caught INT NOT NULL DEFAULT 0,
    whale_shark_caught INT NOT NULL DEFAULT 0,
    ocean_unlocked BOOLEAN NOT NULL DEFAULT FALSE,
    lake_unlocked BOOLEAN NOT NULL DEFAULT FALSE,
    river_unlocked BOOLEAN NOT NULL DEFAULT FALSE,
    coral_reef_unlocked BOOLEAN NOT NULL DEFAULT FALSE,
    deep_sea_unlocked BOOLEAN NOT NULL DEFAULT FALSE,
    bluntnose_minnows_caught INT NOT NULL DEFAULT 0,
    congo_tetra_school_caught INT NOT NULL DEFAULT 0,
    crawfish_caught INT NOT NULL DEFAULT 0,
    yellow_goby_school_caught INT NOT NULL DEFAULT 0,
    current_darter_school_caught INT NOT NULL DEFAULT 0,
    blue_goby_school_caught INT NOT NULL DEFAULT 0,
    atlantic_needlefish_caught INT NOT NULL DEFAULT 0,
    black_sea_bass_caught INT NOT NULL DEFAULT 0,
    red_rainbowfish_caught INT NOT NULL DEFAULT 0,
    turquoise_rainbowfish_caught INT NOT NULL DEFAULT 0,
    blue_catfish_caught INT NOT NULL DEFAULT 0,
    belted_crawfish_caught INT NOT NULL DEFAULT 0,
    river_lamprey_caught INT NOT NULL DEFAULT 0,
    pink_river_dolphin_caught INT NOT NULL DEFAULT 0,
    goonch_catfish_caught INT NOT NULL DEFAULT 0,
    school_of_sardines_caught INT NOT NULL DEFAULT 0,
    crown_jellyfish_caught INT NOT NULL DEFAULT 0,
    lanternfish_caught INT NOT NULL DEFAULT 0,
    barreleye_caught INT NOT NULL DEFAULT 0,
    gulper_eel_caught INT NOT NULL DEFAULT 0,
    glass_octopus_caught INT NOT NULL DEFAULT 0,
    galaxyfish_caught INT NOT NULL DEFAULT 0,
    percula_clownfish_caught INT NOT NULL DEFAULT 0,
    firefish_goby_school_caught INT NOT NULL DEFAULT 0,
    royal_gramma_caught INT NOT NULL DEFAULT 0,
    yellow_boxfish_caught INT NOT NULL DEFAULT 0,
    longspine_porcupinefish_caught INT NOT NULL DEFAULT 0,
    yellow_banded_possum_wrasse_caught INT NOT NULL DEFAULT 0,
    bartlett_anthia_caught INT NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id)
);