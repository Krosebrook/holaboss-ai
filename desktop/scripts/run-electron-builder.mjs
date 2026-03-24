import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const desktopRoot = path.resolve(scriptDir, "..");
const electronBuilderBin = path.join(desktopRoot, "node_modules", ".bin", process.platform === "win32" ? "electron-builder.cmd" : "electron-builder");

function versionFromReleaseTag(releaseTag) {
  const trimmed = releaseTag?.trim();
  if (!trimmed) {
    return "";
  }

  const match = trimmed.match(/(\d+\.\d+\.\d+)$/);
  return match ? match[1] : "";
}

const explicitVersion = process.env.HOLABOSS_APP_VERSION?.trim() || "";
const releaseTagVersion = versionFromReleaseTag(process.env.HOLABOSS_RELEASE_TAG);
const buildVersion = explicitVersion || releaseTagVersion;
const cliArgs = process.argv.slice(2);
const builderArgs = [...cliArgs];

if (buildVersion) {
  builderArgs.push(`-c.extraMetadata.version=${buildVersion}`);
  builderArgs.push(`-c.buildVersion=${buildVersion}`);
  process.stdout.write(`[electron-builder] using app version ${buildVersion}\n`);
}

const child = spawn(electronBuilderBin, builderArgs, {
  cwd: desktopRoot,
  env: process.env,
  stdio: "inherit"
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 1);
});

