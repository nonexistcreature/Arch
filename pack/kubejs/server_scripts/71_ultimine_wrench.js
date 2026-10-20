// Arkhaven: complaint #2 (shxtai). Dismantling Create blocks with the wrench while Ultimine is held kept one block
// and deleted the rest, so Ultimine never activates with the wrench in hand.
ServerEvents.tags('item', e => {
  e.add('ftbultimine:excluded_tools/strict', 'create:wrench')
})
