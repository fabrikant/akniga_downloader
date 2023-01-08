import { clearLine } from 'readline';
import { cursorTo } from 'readline';
import { createWriteStream, mkdirSync } from 'fs';
import https from 'https';



/**
 * Prints download progress to console.
 * @param {Number} progress Float between 0 - 1
 */
function printProgress(progress) {

    progress = Math.round(progress * 100);

    let completePart = '';
    let uncompletePart = '';

    for (let i = 0; i < progress; i++) {
        if (i % 2 == 0) completePart += '█';
    }

    for (let i = 0; i < 100 - progress; i++) {
        if (i % 2 == 1) uncompletePart += ' ';
    }

    let progressBar = `|${completePart}${uncompletePart}| ${progress}%`;

    // process.stdout.clearLine and -||-.cursorTo aren't defined  
    // when stdout of this process is not tied to tty. 
    // That is the case when we launch this app using npm start.
    // That's why here i use readline's clearLine and cursorTo methods.
    clearLine(process.stdout, 0);
    cursorTo(process.stdout, 0);
    process.stdout.write(progressBar);
}

/**
 * Downloads a single file and saves it into 'dlDir'.
 * Optional 3rd parameter 'options' is an object with two parameters:
 *  silent: Wether to print download info to console or not (default is false),
 *  printURL: Wether to print URL to console or not (default is true),
 * @param {String} dlDir Directory to which to save the file. Must already exist.
 * @param {String} url Resource URL.
 * @param {Boolean} options Additional parameters.
 * @returns Promise which resolves to boolean.
 */
function download(dlDir, url, options = {}) {

    const defOptions = { silent: false, printURL: true };
    const { silent, printURL } = { ...defOptions, ...options };
    dlDir += dlDir.endsWith('/') ? '' : '/';

    return new Promise(resolve => {

        https.get(url, res => {

            if (res.statusCode !== 200) {
                console.error('Error while attempting to download. Error code: ' + res.statusCode);
                return resolve(false);
            }
            
            const fileName = url.split('/').pop();
            const file = createWriteStream(dlDir + fileName);
            const fileSize = Number.parseInt(res.headers['content-length']);
            let chunkSizeSum = 0;

            if (!silent && printURL) console.log(printURL);

            res.on('data', chunk => {
                file.write(chunk, () => {
                    chunkSizeSum += chunk.length;
                    if (!silent) printProgress(chunkSizeSum / fileSize);
                });
            });

            res.on('end', () => file.end());

            file.on('finish', () => {
                if (!silent) console.log();
                return resolve(true);
            });
        });
    });
}

/**
 * Downloads files specified in the 'urls' array saving them into 'dlDir'.
 * Optional 3rd parameter 'options' is an object with three parameters:
 *  silent: Wether to print download info to console or not (default is false),
 *  printURL: Wether to print URL to console or not (default is true),
 *  skip: Wether to skip unsuccessful URLs or not (default is false).
 * @param {String} dlDir Directory to which to save the files.
 * @param {Array<String>} urls URLs of desired files.
 * @param {Boolean} options Additional parameters.
 * @returns Promise which resolves to boolean.
 */
async function downloadAll(dlDir, urls, options = {}) {

    const defOptions = { silent: false, printURL: true, skip: false };
    options = {...defOptions, ...options};

    mkdirSync(dlDir, {recursive: true});

    for (const url of urls) {
        const dlSuccess = await download(dlDir, url, options);
        if (!dlSuccess && !options.skip) return false;
    }

    return true;
}

export { download, downloadAll };
