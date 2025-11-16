# API Differences: ON511 vs NB511

## Endpoint URLs

### ON511
- API: `https://511on.ca/api/v2/get/event`
- Map: `https://511on.ca/map#{URLType}-{event['ID']}`
- **No authentication required**

### NB511
- API: `https://511.gnb.ca/api/v2/get/event`
- Map: `https://511.gnb.ca/map#{URLType}-{event['ID']}`
- **Requires API key** (passed as `key` query parameter)

## Authentication

### ON511
- No authentication required
- Public API access

### NB511
- **Required**: Developer API key
- Key must be obtained by registering at https://511.gnb.ca/developers/doc
- Key passed as query parameter: `?key=YOUR_API_KEY`
- Rate limiting: Up to 10 calls per 60 seconds

## Request Parameters

### ON511
- No parameters required
- Optional: format (xml/json), lang (en/fr)

### NB511
- **Required**: `key` (Developer Key)
- Optional: `format` (xml/json, default: json)
- Optional: `lang` (en/fr, default: en)

## Response Structure

### Common Fields (Both APIs)
Both APIs return similar structures with these fields:
- `ID` (integer)
- `RoadwayName` (string)
- `DirectionOfTravel` (string)
- `Description` (string)
- `Reported` (integer, Unix timestamp)
- `LastUpdated` (integer, Unix timestamp)
- `StartDate` (integer, Unix timestamp)
- `PlannedEndDate` (integer, Unix timestamp or null)
- `Latitude` (double)
- `Longitude` (double)
- `EventType` (string: "closures", "accidentsAndIncidents", "roadwork", etc.)
- `IsFullClosure` (boolean)
- `Comment` (string or null)

### NB511 Additional Fields
- `SourceId` (string)
- `Organization` (string)
- `LatitudeSecondary` (double or null)
- `LongitudeSecondary` (double or null)
- `EventSubType` (string)
- `Severity` (string)
- `LanesAffected` (string)
- `EncodedPolyline` (string or null)
- `Restrictions` (object with Width, Height, Length, Weight, Speed)
- `DetourPolyline` (string or null)
- `DetourInstructions` (string or null)
- `Recurrence` (string)
- `RecurrenceSchedules` (string)

### Potential Differences
1. **EventType values**: NB511 may have additional event types (e.g., "flooding" seen in examples)
2. **DirectionOfTravel**: NB511 examples show "North" instead of "Northbound" - need to verify all possible values
3. **Additional metadata**: NB511 provides more detailed information (Organization, EventSubType, Severity)

## Implementation Notes

1. **API Key Management**: Store API key in config file or environment variable
2. **Error Handling**: Handle 401/403 errors for invalid/missing API keys
3. **Rate Limiting**: Implement throttling (max 10 calls per 60 seconds)
4. **Field Mapping**: Code should handle both ON511 and NB511 field structures gracefully
5. **Backward Compatibility**: Consider maintaining support for both APIs if needed

