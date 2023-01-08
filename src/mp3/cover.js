import { mkdirSync } from 'fs';
import cp from 'child_process';
import { promisify } from 'util';
import { moveUp } from './utils.js';

const exec = promisify(cp.exec);



/**
 * Adds cover art to an mp3 file while leaving the original file unmodified.
 * The new mp3 file gets copied into a /cover folder which gets created in 
 * the same directory as the original mp3. 
 * @param {String} filePath Path to the mp3 file.
 * @param {String} imgPath Path to the cover image.
 * @returns Promise which resolves to true once done.
 */
async function mp3addCover(filePath, imgPath) {
    
    const fName = filePath.split('/').pop();
    const cwd = moveUp(filePath);
    
    mkdirSync(cwd + '/cover', {recursive: true});

    await exec(getCommand(fName, imgPath), { cwd });

    return true;
}

function getCommand(fName, imgPath) {
    return `ffmpeg -i "${fName}" -i "${imgPath}" -map 0:0 -map 1:0 -acodec copy -id3v2_version 3 -metadata:s:v title="Album cover" -metadata:s:v comment="Cover (front)" "cover/${fName}"`
}

export default mp3addCover;
