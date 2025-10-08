from .items import WEAPONS

def attack(player, world, target=None):
    # find wildlife in your chunk near you
    ch = world.chunk_of(player.x, player.z)
    weapon = player.equipped if player.equipped in WEAPONS else "rock"
    dmg = WEAPONS[weapon]["dmg"]

    nearest = None
    best = 999
    for w in ch.wildlife:
        dist = abs(w.x-player.x)+abs(w.z-player.z)
        if dist < best:
            best = dist
            nearest = w

    if nearest is None or best>2:
        return "You swing at the air. Nothing is close."

    nearest.hp -= dmg
    out = f"You hit the {nearest.species} for {dmg}. (HP now {max(0, nearest.hp)})"
    if nearest.hp<=0:
        ch.wildlife.remove(nearest)
        player.add_item("meat", 1)
        out += " It dies. You harvest meat."
    else:
        # Counterattack
        player.stats.health -= 5
        out += " It lashes back! (-5 health)"
    return out
