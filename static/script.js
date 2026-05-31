// cofirmation alert before deleting
const delete_transaction = document.querySelector("#delete_transaction")
if (delete_transaction) {
    delete_transaction.addEventListener("submit", function(event) {
   event.preventDefault();
    const bool = confirm("Are you sure you want to delete?")
    if (bool) {
        event.target.submit();
    }
})
}


// search history for every input
const search_input = document.querySelector("#filter_search")
if (search_input) {
    search_input.addEventListener("input", function(event) {
    const rows = document.querySelectorAll(".transaction-card");
    rows.forEach(function(rows) {
        const searchText = event.target.value.toLowerCase();
        const search = rows.textContent.toLowerCase().includes(searchText);
        if (search) {
            rows.style.display = "";
        }
        else
            rows.style.display = "none";
    })
})
}


const toggle = document.querySelector("#theme-toggle");
const body = document.body;

// Set initial state from localStorage
if (localStorage.getItem('theme') === 'dark') {
  body.classList.add('dark-mode');
  toggle.checked = true;
}

// Toggle on change
toggle.addEventListener('change', () => {
  body.classList.toggle('dark-mode');
  localStorage.setItem('theme', toggle.checked ? 'dark' : 'light');
});









