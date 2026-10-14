// TEST ONLY: dumps registry ids to kubejs/exported/registry.json for tools/validate_refs.py
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
  event.server.recipeManager.getRecipes().forEach(h => { const id = String(h.id()); if (id.startsWith('arkhaven:')) data.recipes_arkhaven.push(id) })
  JsonIO.write('kubejs/exported/registry.json', data)
  console.info('ARKHAVEN_REGISTRY_DUMP items=' + data.item.length)
})
