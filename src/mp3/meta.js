import { mkdirSync } from 'fs';
import cp from 'child_process';
import { promisify } from 'util';
import { moveUp } from './utils.js';

const exec = promisify(cp.exec);



/**
 * Copies an mp3 file to a /meta folder while adding metadata to the copied file. 
 * The /meta folder gets created in the directory of the file.
 * @param {String} filePath Path to the file.
 * @param {Object} mData Object specifying what metadata to add.
 * @returns Promise which resolves to true once done.
 */
async function mp3addMeta(filePath, mData) {

    const fName = filePath.split('/').pop();
    const cwd = moveUp(filePath);

    mkdirSync(cwd + '/meta', {recursive: true});
    
    await exec(getCommand(fName, mData), { cwd });

    return true;
}

function getCommand(fName, mData) {

    let mDataStr = '';

    for (const [key, value] of Object.entries(mData)) {
        mDataStr += `-metadata ${key}="${typeof(value) == 'string' ? value.trim() : value}" `
    }

    return `ffmpeg -i "${fName}" -acodec copy ${mDataStr} "meta/${fName}"`;
}

export default mp3addMeta;
