// pad.mjs <master.png> <out.png>: the 3:1 banner centered on a 1920x1080 canvas
// (16:9, what the video model takes), padded with the average colour of the image's top edge.
import { sharp } from "./sharp.mjs";

const [, , input, output] = process.argv;
const { width } = await sharp(input).metadata();
const top = await sharp(input).extract({ left: 0, top: 0, width, height: 8 }).stats();
const [r, g, b] = top.channels.map((channel) => Math.round(channel.mean));
await sharp(input)
  .resize(1920, 640, { fit: "cover" })
  .extend({ top: 220, bottom: 220, left: 0, right: 0, background: { r, g, b } })
  .png()
  .toFile(output);
console.log(output, `bg rgb(${r},${g},${b})`);
