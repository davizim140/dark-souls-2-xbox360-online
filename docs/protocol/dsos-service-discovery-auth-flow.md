# DSOS service discovery and authentication chain

## Scope

This records the connection sequence implemented by the upstream DSOS PC
client emulator in `Source/Server/Client/Client.cpp` and the game service
implementation. It is not proof of the retail Xbox 360 client's sequence.
Do not reuse credentials, tokens, keys, endpoints, or packet formats from
this reference to impersonate an account or redirect a console.

## Upstream PC-emulator sequence

1. **Login service over TCP**
   - Connects to configured `ServerIP:ServerPort`.
   - Sends `RequestQueryLoginServerInfo` with Steam ID and app version.
   - Receives the auth service IP and port in the response.
   - Disconnects the login TCP connection.

2. **Authentication service over TCP**
   - Connects to the returned auth service address.
   - Generates a random 16-byte CWC key.
   - Sends `RequestHandshake` with that key; temporarily disables the message
     cipher for the handshake response.
   - Enables the TCP CWC cipher after receiving a 27-byte response.
   - Sends `GetServiceStatus` with service ID, Steam ID and app version.
   - Generates 8 bytes of random game-key material and sends it as
     `KeyMaterial`; receives a 16-byte game CWC key.
   - Sends a Steam auth ticket prefixed with the 16-byte game CWC key.
   - Receives a game-server information structure containing an auth token,
     game-server IP and UDP port.
   - Disconnects the auth TCP connection.

3. **Game service over UDP**
   - Opens UDP to the address and port returned by auth.
   - Sends the auth token as the initial connection prefix; the server peeks
     this token and rejects unknown/expired tokens.
   - Creates the reliable-UDP stream using the negotiated game CWC key and
     auth token.
   - Performs the FRPG2 SYN handshake using the Steam ID.
   - Only after the reliable-UDP stream is established does the PC emulator
     send `RequestWaitForUserLogin` as a protobuf message.

## Server-side checks

The upstream game service keeps authentication state containing the token,
CWC key and last-refresh time. Its UDP service checks the initial token against
that state before accepting a client. The game client refreshes the token while
active; expired authentication states are removed.

The UDP stream constructs directional CWC client/server cipher objects from
the key and token. Therefore, the game UDP traffic is not just a plaintext
reliable-UDP header followed by protobuf bytes.

## Compatibility implications for Xbox 360

The PC emulator's connection chain depends on:
- a login TCP service and a returned auth-service address;
- an auth TCP handshake and service-status exchange;
- Steam authentication ticket acquisition and validation;
- negotiated 16-byte game CWC key material and a server-issued auth token;
- a UDP game service which validates that token before FRPG2 SYN;
- Steam ID in the subsequent reliable-UDP SYN and protobuf login.

The Xbox 360 build may use a different platform identity, ticket mechanism,
service discovery, key exchange, transport, or endpoint selection. Its failure
message after calibrations does not identify which stage failed. We currently
have no Xbox packet trace or executable evidence to map that failure to any
one stage.

## Safe project status

- No Xbox endpoint or port has been inferred from this PC code.
- No console DNS, router, or network settings should be changed based on this
  document.
- Do not substitute an XUID for Steam ID without protocol evidence.
- Do not attempt to reuse a PC Steam ticket, auth token, or CWC key on Xbox.
- The next Xbox-specific evidence must come from a passive, sanitized
  observation of the console's own connection attempt, or from static analysis
  of the exact Xbox executable. If neither is available, the correct result is
  to keep the Xbox protocol marked unknown rather than invent compatibility.
