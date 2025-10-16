function uploadVideo(){
    const title = document.getElementById("title").ariaValueMax;
    const fileInput = document.getElementById('videoInput');
    const file = fileInput.files[0];

    if(!file){
        alert("please select a video file");
        return;
    }

    let formData = new FormData()
    formData.append("title", title);
    formData.append("video", file)

    fetch("/upload-video/",{
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data =>{
        if (data.video_url){
            alert("Uploade successfully!");
            console.log("Video saved at:", data.video_url);
        }else{
            alert("Upload failed");
        }
    }).catch(err => console.error("Error: ", err));

}

function preview(){
    const fileInput = document.getElementById('videoInput');
    const file = fileInput.files[0];

    const preview = document.getElementById("videoPreview");
    preview.src = URL.createObjectURL(file)
}

function deletePreview() {
    const preview = document.getElementById("videoPreview");
    preview.removeAttribute("src");   
    preview.load();                   
    document.getElementById("videoInput").value = "";
}