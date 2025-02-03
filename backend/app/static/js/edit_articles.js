document.addEventListener("DOMContentLoaded", function () {
    const editArticleModal = new bootstrap.Modal(document.getElementById('editArticleModal'));
    const editForm = document.getElementById('editArticleForm');
    
  
    // When an edit button is clicked…
    document.querySelectorAll('.edit-article-btn').forEach(btn => {
      btn.addEventListener('click', async function(e) {
        e.preventDefault();


        const postId = this.getAttribute('data-post-id');
  
        // Fetch the full article details from the backend
        const response = await fetch(`/admin/get-article/${postId}`);
        if (!response.ok) {
          alert("Erreur lors de la récupération des détails de l'article");
          return;
        }
        const postData = await response.json();

        
        // Populate text inputs and textareas
        document.getElementById('id').value = postData.id;
        document.getElementById('image').src = postData.header_image;
        document.getElementById('title').value = postData.title;
        document.getElementById('author').value = postData.author
        document.getElementById('about_author').value = postData.about_author;
        document.getElementById('date').value = postData.publication_date.split("T")[0]; 
        document.getElementById('reading_time').value = postData.reading_time;
        document.getElementById('introduction').value = postData.introduction;
        document.getElementById('section_1_title').value = postData.section_1_title;
        document.getElementById('section_1_content').value = postData.section_1_content;
        document.getElementById('quote').value = postData.quote || "";
        document.getElementById('section_2_title').value = postData.section_2_title;
        document.getElementById('section_2_content').value = postData.section_2_content;
        document.getElementById('tools').value = postData.tools || "";
        document.getElementById('section_3_title').value = postData.section_3_title;
        document.getElementById('section_3_content').value = postData.section_3_content;
        document.getElementById('conclusion').value = postData.conclusion;
        document.getElementById('cta').value = postData.cta || "";
  
        // Show the modal for editing
        editArticleModal.show();
      });
    });




// Optional: handle the form submission with Cloudinary upload if a new image is selected.


  editForm.addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(editForm);
    const postId = formData.get("id");
    
    // Check if a new image file was selected
    const imageFile = document.getElementById('image').files[0];
    if (imageFile) {
      // Upload image to Cloudinary
      const cloudinaryForm = new FormData();
      cloudinaryForm.append("file", imageFile);
      cloudinaryForm.append("upload_preset", "my_preset");
      cloudinaryForm.append("folder", "blog_images");

      const cloudinaryResponse = await fetch("https://api.cloudinary.com/v1_1/dfsw4wv22/image/upload", {
          method: "POST",
          body: cloudinaryForm
      });
      const cloudinaryData = await cloudinaryResponse.json();
      if (!cloudinaryData.secure_url) {
          alert("Échec de l'upload de l'image sur Cloudinary");
          return;
      }
      // Update header image URL in form data
      formData.set("header_image", cloudinaryData.secure_url);
      // Optionally remove the file field if your backend expects only the URL.
      formData.delete("image");
    } else {
      // If no new image is selected, use the current image URL
      formData.set("header_image", document.getElementById('current-header-image').src);
    }

    // Submit the updated data to your backend update endpoint.
    const updateResponse = await fetch(`/admin/update-article/${postId}`, {
      method: "POST",
      body: formData
    });

    if (updateResponse.ok) {
      alert("Article mis à jour !");
      location.reload(); // Refresh page to show updated data
    } else {
      const errorData = await updateResponse.json();
      alert("Erreur lors de la mise à jour de l'article : " + errorData.detail);
    }
  });
});