let pc;

async function startStreaming() {
    pc = new RTCPeerConnection();

    // Create an audio track
    const audioTrack = pc.addTransceiver("audio").receiver.track;
    const audioPlayer = document.getElementById("audioPlayer");
    audioPlayer.srcObject = new MediaStream([audioTrack]);

    // Connect to the signaling server
    const signalingUrl = "ws://localhost:8080/ws";
    const signalingSocket = new WebSocket(signalingUrl);

    signalingSocket.onopen = async () => {
        // Send an offer to the server
        console.log( "Sending 'offer'" )
        signalingSocket.send("offer");
    };

    signalingSocket.onmessage = async (event) => {
        const message = JSON.parse(event.data);

        if (message.type === "answer") {
            // Set the remote description
            await pc.setRemoteDescription(new RTCSessionDescription(message));
        }
    };

    // Start consuming audio frames
    const audioReader = new MediaStreamTrackProcessor(audioTrack);
    audioReader.ondata = (event) => {
        // Process the received audio frame here
        const audioFrame = event.data;
        console.log("Received audio frame:", audioFrame);
    };

    // Listen for ICE candidates and send them to the server
    pc.onicecandidate = (event) => {
        console.log( "Got ICE candidate, sending shit to backend" )
        if (event.candidate) {
            signalingSocket.send(JSON.stringify({
                type: "candidate",
                candidate: event.candidate.toJSON()
            }));
        }
    };

    // Create an offer and set it as the local description
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    signalingSocket.send(JSON.stringify(pc.localDescription));
}

function stopStreaming() {
    pc.close();
}

window.addEventListener("unload", () => {
    if (pc) {
        pc.close();
    }
});
