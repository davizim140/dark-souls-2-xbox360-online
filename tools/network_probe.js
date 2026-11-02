const dns = require("node:dns").promises;
const net = require("node:net");
const dgram = require("node:dgram");

const HOST = process.env.DS2_HOST || "us-lax02.altare.global";
const PORT = Number(process.env.DS2_PORT || "25465");
const TIMEOUT_MS = 7000;

function tcpProbe() {
  return new Promise(async (resolve) => {
    const socket = net.createConnection({ host: HOST, port: PORT });
    let received = "";
    let finished = false;
    const finish = (ok, detail) => {
      if (finished) return;
      finished = true;
      socket.destroy();
      console.log(`TCP ${ok ? "PASS" : "FAIL"}: ${detail}`);
      resolve(ok);
    };
    socket.setTimeout(TIMEOUT_MS);
    socket.on("connect", () => {
      console.log("TCP: conexão externa estabelecida");
      socket.write("external-probe");
    });
    socket.on("data", (chunk) => {
      received += chunk.toString("utf8");
      if (received.includes("DS2 TCP TEST: OK")) {
        finish(true, "banner recebido do processo Altare");
      }
    });
    socket.on("timeout", () => finish(false, "timeout aguardando resposta"));
    socket.on("error", (error) => finish(false, error.message));
    socket.on("end", () => {
      if (!finished) finish(false, "conexão encerrada sem banner esperado");
    });
  });
}

function udpProbe() {
  return new Promise((resolve) => {
    const socket = dgram.createSocket("udp4");
    let finished = false;
    const finish = (ok, detail) => {
      if (finished) return;
      finished = true;
      clearTimeout(timer);
      socket.close();
      console.log(`UDP ${ok ? "PASS" : "FAIL"}: ${detail}`);
      resolve(ok);
    };
    const timer = setTimeout(
      () => finish(false, "sem resposta UDP dentro do prazo"),
      TIMEOUT_MS
    );
    socket.on("message", (message) => {
      const response = message.toString("utf8");
      finish(
        response.includes("DS2 UDP TEST: OK"),
        response.includes("DS2 UDP TEST: OK")
          ? "resposta recebida do processo Altare"
          : `resposta inesperada: ${response}`
      );
    });
    socket.on("error", (error) => finish(false, error.message));
    socket.send(Buffer.from("external-probe"), PORT, HOST, (error) => {
      if (error) finish(false, error.message);
      else console.log("UDP: pacote enviado para o endpoint público");
    });
  });
}

(async () => {
  console.log(`Alvo: ${HOST}:${PORT}`);
  try {
    const result = await dns.lookup(HOST);
    console.log(`DNS PASS: ${HOST} -> ${result.address}`);
  } catch (error) {
    console.log(`DNS FAIL: ${error.message}`);
    process.exit(1);
  }

  const [tcpOk, udpOk] = await Promise.all([tcpProbe(), udpProbe()]);
  console.log("--- RESULTADO ---");
  console.log(`TCP: ${tcpOk ? "PASS" : "FAIL"}`);
  console.log(`UDP: ${udpOk ? "PASS" : "FAIL"}`);
  if (!tcpOk || !udpOk) process.exit(1);
})();
