//Variables declaration for modal DOM use.
const modal = document.getElementById('modalContainer');
const modalCloseBtn = document.getElementById('modalClose');
const modalOpenBtn = document.getElementById('modalOpen');
 
// To open modal when the instruction button is clicked.
function modalOpen(evt) {
          if (evt.target === modalOpenBtn) {
               modal.style.display='block';     
          }
     }    
modalOpenBtn.addEventListener('click', modalOpen);

// To close modal when the close button is clicked.
function modalClose(evt) {
          if (evt.target === modalCloseBtn) {
             modal.style.display='none';     
          }
}
modalCloseBtn.addEventListener('click', modalClose);
