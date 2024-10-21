document.addEventListener('DOMContentLoaded', function() {
    const likeIcon = document.getElementById('likeIcon');
    const collectionIcon = document.getElementById('collectionIcon');

    likeIcon.addEventListener('click', function() {
        if (likeIcon.src.includes('like.png')) {
            likeIcon.src = '/static/images/like1.png';
        } else {
            likeIcon.src = '/static/images/like.png';
        }
    });

    collectionIcon.addEventListener('click', function() {
        if (collectionIcon.src.includes('collection.png')) {
            collectionIcon.src = '/static/images/collection1.png';
        } else {
            collectionIcon.src = '/static/images/collection.png';
        }
    });
});

document.getElementById('post-image').addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const imgPreview = document.createElement('img');
            imgPreview.src = e.target.result;
            imgPreview.className = 'post-image-preview';
            document.getElementById('createPostModal').appendChild(imgPreview);
        }
        reader.readAsDataURL(file);
    }
});

document.getElementById('post-image').addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const imgPreview = document.createElement('img');
            imgPreview.src = e.target.result;
            imgPreview.className = 'post-image-preview';
            document.getElementById('createPostModal').appendChild(imgPreview);
        }
        reader.readAsDataURL(file);
    }
});

document.getElementById('post-video').addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const videoPreview = document.createElement('video');
            videoPreview.src = e.target.result;
            videoPreview.className = 'post-video-preview';
            videoPreview.controls = true;
            document.getElementById('createPostModal').appendChild(videoPreview);
        }
        reader.readAsDataURL(file);
    }
});
