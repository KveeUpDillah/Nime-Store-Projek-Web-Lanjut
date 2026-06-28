let collapsed = false;
function toggleSidebar() {
  collapsed = !collapsed;
  document.getElementById('sidebar').classList.toggle('collapsed', collapsed);
  document.body.classList.toggle('sidebar-collapsed', collapsed);
  document.getElementById('toggle-icon').className = collapsed
    ? 'ti ti-layout-sidebar-left-expand'
    : 'ti ti-layout-sidebar-left-collapse';
}

function confirmDelete(event, label) {
  event.preventDefault();
  const form = event.target;
  Swal.fire({
    title: 'Hapus data ini?',
    text: label ? `"${label}" akan dihapus secara permanen.` : 'Data ini akan dihapus secara permanen.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#dc2626',
    cancelButtonColor: '#6b7280',
    confirmButtonText: 'Ya, hapus',
    cancelButtonText: 'Batal',
    reverseButtons: true
  }).then((result) => {
    if (result.isConfirmed) {
      form.submit();
    }
  });
  return false;
}