// Arkhaven key layout. Mod defaults collide badly (18 actions on V, 9 on B, R = reload + roll + spell wheel...).
// Layers: plain keys = things pressed all the time; ALT = social & origin powers; CONTROL = armor/equipment modes;
// SHIFT = tool-in-hand extras. Context-only overlaps (JEI/quest-editor GUI keys, vehicle keys) are left alone.
// TACZ, Ars Nouveau and the Supplementaries quiver IGNORE modifiers (they compare raw key codes / KeyMapping.matches),
// so they get plain keys; their keys only fire with their item in hand, so they are separated by context instead
// (gun: R/Y/N/X/C, Ars caster: C/X/N, bow+quiver: X). v2 = this fix (v1 put them on Alt/Ctrl/Shift).
// Applied ONCE per layout version (players' later rebinds survive); bump ARK_KEYS_VERSION after changing the table.
// Cheat sheet for players: quest chapter "Памятка игрока" -> "Клавиши".
let ARK_KEYS_VERSION = 2
let ARK_KEYS = {
  // plain: everyday actions (also pinned, so old installs get them back)
  'key.sophisticatedbackpacks.open_backpack': 'b',
  'key.curios.open.desc': 'g',
  'accessories.key.open_accessories_screen': 'h',
  'key.aether.open_accessories.desc': 'i',
  'key.ftbquests.quests': 'l',
  'gui.xaero_open_map': 'm',
  'key.puffish_skills.open': 'p',
  'gui.xaero_waypoints_key': 'u',
  'key.neoorigins.view_info': 'o',
  'iris.keybind.toggleShaders': 'k',
  'key.irons_spellbooks.spellbook_cast': 'v',
  'key.irons_spellbooks.spell_wheel': 'r',
  'key.ftbultimine': 'grave.accent',
  'keybinds.combat_roll.roll': 'z',
  'key.ars_nouveau.selection_hud': 'c',
  'key.ars_nouveau.next_slot': 'x',
  'key.jetpack.toggle_active.description': 'j',
  'key.emotecraft.fastchoose': 'period',
  'dmr.keybind.summon_dragon': 'comma',
  'key.easy_villagers.pick_up': 'semicolon',
  // ALT: social, map, origin powers, curio bags
  'key.neoorigins.skill_1': '1:ALT',
  'key.neoorigins.skill_2': '2:ALT',
  'key.neoorigins.skill_3': '3:ALT',
  'key.neoorigins.skill_4': '4:ALT',
  'key.neoorigins.class_skill': '5:ALT',
  'key.neoorigins.toggle_night_vision': 'k:ALT',
  'key.push_to_talk': 'caps.lock',
  'key.voice_chat': 'v:ALT',
  'key.mute_microphone': 'm:ALT',
  'gui.xaero_new_waypoint': 'u:ALT',
  'key.shouldersurfing.swap_shoulder': 'o:ALT',
  'key.ars_nouveau.open_book': 'n',
  'key.occultism.backpack': 'b:ALT',
  'key.occultism.storage_remote': 'n:ALT',
  'key.occultism.ender_bag': 'e:ALT',
  'key.ars_elemental.open_pouch': 'p:ALT',
  'key.jetpack.toggle_hover.description': 'j:ALT',
  'key.aether.invisibility_toggle.desc': 'i:ALT',
  'key.immersiveengineering.magnetEquip': 's:ALT',
  'key.tacz.fire_select.desc': 'n',
  'key.tacz.inspect.desc': null,
  'key.tacz.refit.desc': 'y',
  'key.ars_nouveau.head_curio_hotkey': 'y',
  'key.tacz.melee.desc': 'MOUSE:4',
  // CONTROL: armor and equipment modes
  'key.mekanism.head_mode': 'h:CONTROL',
  'key.mekanism.chest_mode': 'g:CONTROL',
  'key.mekanism.legs_mode': 'j:CONTROL',
  'key.mekanism.feet_mode': 'b:CONTROL',
  'key.cataclysm.helmet_ability': 'c:CONTROL',
  'key.cataclysm.chestplate_ability': 'y:CONTROL',
  'key.cataclysm.boots_ability': 'v:CONTROL',
  'key.cataclysm.ability': 'f:CONTROL',
  'key.deep_aether.stratus_dash_ability.desc': 'r:CONTROL',
  'key.deeperdarker.transmit': 't:CONTROL',
  'supplementaries.keybind.quiver': 'x',
  'key.sophisticatedbackpacks.inventory_interaction': 'i:CONTROL',
  'key.tacz.zoom.desc': 'x',
  'create_mobile_packages.keyinfo.open_portable_stock_ticker': 'k:CONTROL',
  'create_mobile_packages.keyinfo.open_player_networks_screen': 'l:CONTROL',
  // SHIFT: extras for the tool in hand
  'key.ars_nouveau.previous_slot': null,
  'key.tacz.crawl.desc': 'c',
  'key.buildinggadgets2.settings_menu': 'g:SHIFT',
  'key.buildinggadgets2.anchor': 'h:SHIFT',
  'key.buildinggadgets2.range': 'r:SHIFT',
  'key.buildinggadgets2.undo': 'u:SHIFT',
  // unbound: rare, reachable from their own menus
  'key.voice_chat_group': null,
  'key.disable_voice_chat': null,
  'key.hide_icons': null,
  'gui.xaero_enlarge_map': null,
  'gui.xaero_minimap_settings': null,
  'key.toastcontrol.clear': null,
  'key.kubejs.kubedex': null,
  'key.mca.skin_library': null,
  'key.socialInteractions': null,
  'iris.keybind.shaderPackSelection': null,
  'iris.keybind.reload': null,
  'key.twilightforest.swap_hotbar': null,
  'key.twilightforest.zoom': null,
  'key.twilightforest.item_display_map_cycle': null,
  'key.deep_aether.toggle_skyjade_transparency': null,
  'key.mekanism.key_hud': null,
  'key.tacz.interact.desc': null,
  'key.immersivepetroleum.projector.flip': null
}

let arkKeysDone = false
NativeEvents.onEvent('net.neoforged.neoforge.client.event.ClientTickEvent$Post', e => {
  if (arkKeysDone) return
  arkKeysDone = true
  let flagPath = 'local/kubejs/arkhaven_keybinds.json'
  let flag = null
  try { flag = JsonIO.read(flagPath) } catch (err) { }
  if (flag && flag.version >= ARK_KEYS_VERSION) return
  let InputConstants = Java.loadClass('com.mojang.blaze3d.platform.InputConstants')
  let KeyModifier = Java.loadClass('net.neoforged.neoforge.client.settings.KeyModifier')
  let KeyMapping = Java.loadClass('net.minecraft.client.KeyMapping')
  let opts = Client.options
  let changed = 0
  opts.keyMappings.forEach(km => {
    let name = '' + km.getName()
    if (!(name in ARK_KEYS)) return
    let spec = ARK_KEYS[name]
    let key = InputConstants.UNKNOWN
    let mod = KeyModifier.NONE
    if (spec !== null) {
      let parts = spec.split(':')
      if (parts[0] === 'MOUSE') key = InputConstants.getKey('key.mouse.' + parts[1])
      else {
        key = InputConstants.getKey('key.keyboard.' + parts[0])
        if (parts.length > 1) mod = KeyModifier.valueOf(parts[1])
      }
    }
    km.setKeyModifierAndCode(mod, key)
    changed++
  })
  KeyMapping.resetMapping()
  opts.save()
  JsonIO.write(flagPath, { version: ARK_KEYS_VERSION })
  console.info('ARK_KEYS applied layout v' + ARK_KEYS_VERSION + ': ' + changed + ' bindings')
})
