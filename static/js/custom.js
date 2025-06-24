/**
 * SweetAlert popup Message
 * @param {strign} mss - message detail
 * @param {strin} tag - tag success or error
 * @param {boolean} isRefresh - check location reload
 */
const PopMessage = (mss, tag, isRefresh = false) => {
  const mssTag = tag;
  const mssMsg = mss;
  const mssHeader = mssTag == "error" ? "Error" : "Success";
  const mssIcon = mssTag == "error" ? "error" : "success";
  const popup = Swal.fire({
    icon: mssIcon,
    title: mssHeader,
    text: mssMsg,
    confirmButtonColor: "#f97316",
  });
  if (isRefresh == true) {
    popup.then(() => {
      location.reload();
    });
  }
};
