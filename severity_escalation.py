evt.component='Oracle Database'

# Initialize existing_count.
existing_count = 0
 
# Prefix for fingerprint (dedupid).
dedupfields = [evt.device, evt.component, evt.eventClass]
 
if 'getFacade' in globals() and getFacade('zep'):
    # Zenoss >=4 method.
    if getattr(evt, 'eventKey', False):
        dedupfields += [evt.eventKey, evt.severity]
    else:
        dedupfields += [evt.severity, evt.summary]
 
    zep = getFacade('zep')
    evt_filter = zep.createEventFilter(
        status=(0,1,2),
        fingerprint='|'.join(map(str, dedupfields)))
 
    summaries = zep.getEventSummaries(0, 1, filter=evt_filter)
    if summaries['total']:
        existing_count = list(summaries['events'])[0]['count']
else:
    # Zenoss <4 method.
    if getattr(evt, 'eventKey', False):
        dedupfields += [evt.eventKey, evt.severity]
    else:
        dedupfields += [evt.eventKey, evt.severity, evt.summary]
 
    em = dmd.Events.getEventManager()
    em.cleanCache()
    try:
        db_evt = em.getEventDetail(dedupid='|'.join(map(str, dedupfields)))
        existing_count = db_evt.count
    except Exception:
        pass
 
# Do what you like with the count and event;
# In this example we up the severity to CRITICAL if the count is >= 2
if existing_count >= 2:
    evt.severity = 5