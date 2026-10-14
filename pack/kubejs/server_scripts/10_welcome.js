// Arkhaven: first-join hint (server-side; text key resolved by client lang).
PlayerEvents.loggedIn(event => {
  if (!event.player.persistentData.arkhavenWelcomed) {
    event.player.persistentData.arkhavenWelcomed = true
    event.player.tell(Text.translate('arkhaven.welcome'))
  }
})
