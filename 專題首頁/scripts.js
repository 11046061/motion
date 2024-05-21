document.addEventListener('DOMContentLoaded', function() {
    const likeIcon = document.getElementById('likeIcon');
    const collectionIcon = document.getElementById('collectionIcon');

    likeIcon.addEventListener('click', function() {
        if (likeIcon.src.includes('like.png')) {
            likeIcon.src = 'like1.png';
        } else {
            likeIcon.src = 'like.png';
        }
    });

    collectionIcon.addEventListener('click', function() {
        if (collectionIcon.src.includes('collection.png')) {
            collectionIcon.src = 'collection1.png';
        } else {
            collectionIcon.src = 'collection.png';
        }
    });
});
