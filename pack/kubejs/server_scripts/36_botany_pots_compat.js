// Botany Pots ships pot recipes for vanilla and a few dozen mods, but none for most of ours (Let's Do, Ars, Mystical
// Agriculture, Delight add-ons, ...), so their seeds simply don't go into a pot. Here every modded crop gets one:
// a block that is a plant (BushBlock) with a growth "age" property and a seed item that places it ->
// botanypots:block_derived_crop (Botany Pots reads the drops from the block's own loot table, like for vanilla wheat).
// Crops that already have a Botany Pots recipe are left alone; water crops (rice-like) get the water soil.
ServerEvents.recipes(event => {
  let Reg = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')
  let BushBlock = Java.loadClass('net.minecraft.world.level.block.BushBlock')
  let Item = Java.loadClass('net.minecraft.world.item.Item')
  let Items = Java.loadClass('net.minecraft.world.item.Items')

  let existing = {}
  event.forEachRecipe({ type: 'botanypots:block_derived_crop' }, r => {
    let j = r.json
    if (j && j.has('block')) existing[String(j.get('block').getAsString())] = true
  })

  let added = 0
  Reg.BLOCK.entrySet().forEach(entry => {
    let id = String(entry.getKey().location())
    let block = entry.getValue()
    if (id.startsWith('minecraft:') || existing[id]) return
    if (!(block instanceof BushBlock)) return
    let hasAge = false
    block.getStateDefinition().getProperties().forEach(p => { if (String(p.getName()) === 'age') hasAge = true })
    if (!hasAge) return
    let seed = Item.byBlock(block)
    if (!seed || seed === Items.AIR) return
    let recipe = { type: 'botanypots:block_derived_crop', block: id, input: { item: String(Reg.ITEM.getKey(seed)) } }
    if (/rice|water|lotus|lily|kelp|seagrass|cattail|reed/.test(id)) recipe.soil = { tag: 'botanypots:soil/water' }
    event.custom(recipe).id('arkhaven:botanypots/' + id.replace(':', '/'))
    added++
  })
  console.info('[Arkhaven] Botany Pots: added pot recipes for ' + added + ' modded crops')
})
