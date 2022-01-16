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
    extra_points INT NULL DEFAULT 0,
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