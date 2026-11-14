// sharp is not a dependency of this repo: it is borrowed from a checkout that
// has it installed. SHARP_FROM names that checkout's package.json; the default
// is a maraschio.com checkout next to this one.
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";

const beside = fileURLToPath(new URL("../../../maraschio.com/package.json", import.meta.url));
export const sharp = createRequire(resolve(process.env.SHARP_FROM || beside))("sharp");
