/**
 * Returns new path as string based on some path by moving up the directories.
 * Optional 'levels' tells how many levels to "move up". For example if 'path' is 
 * C:/music/audio.mp3 and 'levels' is 1 it will return C:/music.
 * @param {String} path Some path.
 * @param {Number} levels How many levels to move up.
 * @returns New path.
 */
function moveUp(path, levels = 1) {
    const parts = path.split('/');
    for (; levels > 0; levels--) {
        if (parts.length > 1) parts.pop();
        else break;
    };
    return parts.join('/');
}

export { moveUp };
