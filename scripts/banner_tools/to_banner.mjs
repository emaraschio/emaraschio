// to_banner.mjs <in> <out.webp>: 1800x600 cover WebP, quality stepped down until under 400 KB.
import { statSync } from "node:fs";
import { sharp } from "./sharp.mjs";

const [, , input, output] = process.argv;
for (const quality of [84, 80, 76, 72, 68, 64]) {
  await sharp(input).resize(1800, 600, { fit: "cover", position: "attention" }).webp({ quality, effort: 6 }).toFile(output);
  const kb = Math.round(statSync(output).size / 1024);
  if (kb <= 400) {
    console.log(`${output} ${kb} KB q${quality}`);
    process.exit(0);
  }
}
console.log(`${output} over 400 KB at q64`);
process.exit(1);
