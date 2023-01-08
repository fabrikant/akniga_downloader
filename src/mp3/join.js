import { readdirSync } from 'fs';
import cp from 'child_process';
import { promisify } from 'util';

const exec = promisify(cp.exec);



/**
 * Joins mp3 files using ffmpeg and produces a single big file called 
 * joined.mp3 leaving original files. If 'fNames' array is empty it joins 
 * all mp3 files in the directory in alphabethical order.
 * Note: It doesn't join files called joined.mp3.
 * @param {String} dirPath Path to the directory that holds the files to be joined.
 * @param {Array<String>} fNames If specified joins only these files. Order matters.
 * @returns Promise which resolves to true once done.
 */
async function mp3join(dirPath, fNames = null) {
    fNames = fNames ? fNames : getFileNames(dirPath);
    await exec(getCommand(fNames), {cwd: dirPath});
    return true;
}

function getFileNames(dirPath) {
    const fileNames = readdirSync(dirPath);
    return fileNames.filter(val => val.endsWith('.mp3') && val !== 'joined.mp3');
}

function getCommand(fNames) {
    return `ffmpeg -i "concat:${fNames.join('|')}" -acodec copy -map_metadata -1 joined.mp3`
}

export default mp3join;
