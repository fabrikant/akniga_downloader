import { mkdirSync } from 'fs';
import cp from 'child_process';
import { promisify } from 'util';
import { moveUp } from './utils.js';

const exec = promisify(cp.exec);



/**
 * Splits an mp3 file into smaller tracks using ffmpeg leaving original file intact. 
 * The tracks are saved to /split folder which it creates in the folder of the mp3 file.
 * trackDataArray must hold objects that have at least these properties:
 *  title   (track title), 
 *  start   (track start time in seconds),
 *  end     (track end time in seconds) (Optional. If undefined end of file is assumed.)
 * @param {String} filePath Path to the file.
 * @param {Array<Object>} trackDataArray Array of track data objects.
 * @returns Promise which resolves to true once done.
 */
async function mp3split(filePath, trackDataArray) {
    
    const fName = filePath.split('/').pop();
    const cwd = moveUp(filePath);

    mkdirSync(cwd + '/split', {recursive: true});

    for (const trackData of trackDataArray) {
        await exec(getCommand(fName, trackData), { cwd });
    }

    return true;
}

function getCommand(fName, trackData) {
    const {start, end, title} = trackData;
    return `ffmpeg -i "${fName}" -acodec copy -ss ${start} ${end ? '-to ' + end : ''} -map_metadata -1 "split/${title}.mp3"`
}

export default mp3split;
