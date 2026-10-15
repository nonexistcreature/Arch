// TEST ONLY: dumps registry ids to kubejs/exported/registry.json for tools/validate_refs.py,
// and item stats (armour, weapons, tools) to kubejs/exported/item_stats.json for tools/gen_arsenal.py.
ServerEvents.loaded(event => {
  const R = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')
  const dump = (reg) => { const out = []; reg.keySet().forEach(k => out.push(String(k))); return out }
  const data = {
    item: dump(R.ITEM), block: dump(R.BLOCK), fluid: dump(R.FLUID),
    entity_type: dump(R.ENTITY_TYPE), mob_effect: dump(R.MOB_EFFECT),
    recipe_type: dump(R.RECIPE_TYPE),
    potion: dump(R.POTION),
    recipes_arkhaven: [],
  }
  data.structure = []
  event.server.registryAccess().registryOrThrow(Java.loadClass('net.minecraft.core.registries.Registries').STRUCTURE).keySet().forEach(k => data.structure.push(String(k)))
  event.server.recipeManager.getRecipes().forEach(h => { const id = String(h.id()); if (id.startsWith('arkhaven:')) data.recipes_arkhaven.push(id) })
  JsonIO.write('kubejs/exported/registry.json', data)
  console.info('ARKHAVEN_REGISTRY_DUMP items=' + data.item.length)

  // ---- item stats: attribute modifiers (armour, toughness, attack damage/speed), durability, tool/armour class
  const DC = Java.loadClass('net.minecraft.core.component.DataComponents')
  const ArmorItem = Java.loadClass('net.minecraft.world.item.ArmorItem')
  const TieredItem = Java.loadClass('net.minecraft.world.item.TieredItem')
  const ItemStack = Java.loadClass('net.minecraft.world.item.ItemStack')
  const stats = {}
  let n = 0
  R.ITEM.keySet().forEach(key => {
    const id = String(key)
    try {
      const item = R.ITEM.get(key)
      const st = new ItemStack(item)
      const e = {}
      const mods = st.getAttributeModifiers()
      if (mods) {
        mods.modifiers().forEach(m => {
          const attr = String(m.attribute().unwrapKey().get().location())
          const slot = String(m.slot())
          const short = attr.replace('minecraft:generic.', '').replace('minecraft:', '')
          const k = short + '@' + slot
          e[k] = (e[k] || 0) + Number(m.modifier().amount())
        })
      }
      const dmg = st.get(DC.MAX_DAMAGE)
      if (dmg) e.durability = Number(dmg)
      if (item instanceof ArmorItem) e.armor_slot = String(item.getType().getName())
      if (item instanceof TieredItem) e.tool = String(item.getClass().getSimpleName())
      const food = st.get(DC.FOOD)
      if (food) { e.nutrition = Number(food.nutrition()); e.saturation = Number(food.saturation()) }
      if (Object.keys(e).length) { stats[id] = e; n++ }
    } catch (err) { /* exotic items: skip */ }
  })
  JsonIO.write('kubejs/exported/item_stats.json', stats)
  console.info('ARKHAVEN_ITEM_STATS items=' + n)
})
