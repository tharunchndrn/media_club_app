/// Base URL for the Media Club REST API.
///
/// Defaults to the local dev backend. Note for future reference: when running
/// against an Android emulator (not a physical device or the iOS simulator),
/// `localhost` refers to the emulator itself, not the host machine — use
/// `10.0.2.2` instead (e.g. `http://10.0.2.2:8000/api/v1`). Not solved here,
/// just left as a pointer for whoever wires up build flavors/environments.
const String kApiBaseUrl = 'http://localhost:8000/api/v1';
