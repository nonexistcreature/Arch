// TEST ONLY: checks 65_elites.js and 66_progression_gates.js. Logs ARK_ELITE_TEST / ARK_GATES lines.
ServerEvents.loaded(event => {
  const server = event.server
  const gates = []
  server.recipeManager.getRecipes().forEach(h => { const id = String(h.id()); if (id.startsWith('arkhaven:gate/')) gates.push(id) })
  console.info('ARK_GATES ' + gates.length + ' ' + gates.join(','))
  server.scheduleInTicks(60, () => {
    const s0 = server.overworld().getSharedSpawnPos()
    const s = { x: s0.x + 5000, y: 120, z: s0.z }
    console.info('ARK_ELITE_TEST forceload=' + server.runCommandSilent(`forceload add ${s.x} ${s.z}`))
    server.scheduleInTicks(5, () => {
      for (let i = 0; i < 3; i++) server.runCommandSilent(`summon minecraft:zombie ${s.x + 2 * i} ${s.y} ${s.z}`)
      let n = 0
      server.overworld().getEntities().forEach(en => {
        if (String(en.type).indexOf('zombie') < 0) return
        n++
        if (n <= 2) arkMakeElite(en, n)
        const Attributes = Java.loadClass('net.minecraft.world.entity.ai.attributes.Attributes')
        console.info('ARK_ELITE_TEST tier=' + en.getPersistentData().getInt('ark_elite') + ' hp=' + en.getHealth() + '/' + en.getMaxHealth() +
          ' dmg=' + en.getAttributeValue(Attributes.ATTACK_DAMAGE) + ' head=' + en.getItemBySlot(Java.loadClass('net.minecraft.world.entity.EquipmentSlot').HEAD).getItem())
        en.discard()
      })
    })
  })
})
