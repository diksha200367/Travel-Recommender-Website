const menus = document.querySelector("nav ul");
const header = document.querySelector("header");
const menuBtn = document.querySelector(".menu-btn");
const closeBtn = document.querySelector(".close-btn");

menuBtn.addEventListener("click", ()=>{
    menus.classList.add("display");
});

closeBtn.addEventListener("click", ()=>{
    menus.classList.remove("display");
});

// scroll sticky navbar
window.addEventListener("scroll", ()=>{
    if(document.documentElement.scrollTop>20)
      {
        header.classList.add("sticky");
      }else{
        header.classList.remove("sticky");
      }
  });

  function handleFormSubmit(event) {
    event.preventDefault();

    const fileNameInput = document.getElementById('searchInput').value.trim();
    
    // Check if a file name is provided
    if (fileNameInput) {
        fileName=fileNameInput.toLowerCase();
        // Open the file (assuming it's in the same directory)
        const fileUrl = fileName.endsWith('.html') ? fileName : `${fileName}.html`;
        window.open(fileUrl, '_parent'); // Opens the file in a new tab
    } else {
        alert('Please enter a file name.');
    }
}

// Attach event listener to the button
document.getElementById('searchform').addEventListener('submit', handleFormSubmit);