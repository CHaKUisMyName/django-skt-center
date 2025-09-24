/**
 * SweetAlert popup Message
 * @param {strign} mss - message detail
 * @param {strin} tag - tag success or error
 * @param {boolean} isRefresh - check location reload
 */
const PopMessage = (mss, tag, isRefresh = false, toURL = null) => {
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
  if (toURL) {
    popup.then(() => {
      window.location.href = toURL;
    });
  }
};

// ฟังก์ชันเช็คว่า input มีค่าตรงกับ dd/mm/yyyy หรือไม่
function isValidDateFormat(dateString) {
  const regex = /^(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/\d{4}$/;
  return regex.test(dateString);
}

const initialDatePk = (element) => {
  const dp = new tempusDominus.TempusDominus(element, {
    useCurrent: false, // ไม่ให้มีค่าเริ่มต้นที่อาจผิดพลาด
    localization: {
      format: "dd/MM/yyyy",
      hourCycle: "h24",
    },
    display: {
      buttons: {
        today: true,
        clear: true,
        close: true,
      },
      //sideBySide: true,
      viewMode: "calendar",
      components: {
        decades: true,
        year: true,
        month: true,
        date: true,
        hours: false,
        minutes: false,
        seconds: false,
      },
    },
  });
  return dp;
};
const initialDateTimePk = (element) => {
  const dp = new tempusDominus.TempusDominus(element, {
    useCurrent: false, // ไม่ให้มีค่าเริ่มต้นที่อาจผิดพลาด
    localization: {
      format: "dd/MM/yyyy HH:mm",
      hourCycle: "h24",
    },
    display: {
      // buttons: {
      //   today: true,
      //   clear: true,
      //   close: true,
      // },
      viewMode: "calendar",
      components: {
        decades: true,
        year: true,
        month: true,
        date: true,
        hours: true,
        minutes: true,
        seconds: false,
      },
    },
  });
  return dp;
};

const initialTimePk = (element) => {
  const dp = new tempusDominus.TempusDominus(element, {
    useCurrent: false, // ไม่ให้มีค่าเริ่มต้นที่อาจผิดพลาด
    localization: {
      format: "HH:mm",
      hourCycle: "h24",
    },
    display: {
      // buttons: {
      //   today: true,
      //   clear: true,
      //   close: true,
      // },
      viewMode: "calendar",
      components: {
        decades: true,
        year: false,
        month: false,
        date: false,
        hours: true,
        minutes: true,
        seconds: false,
      },
    },
  });
  return dp;
};

function datePkSetMinDate(el, date) {
  el.updateOptions({
    restrictions: {
      minDate: date,
    },
  });
}
const getAPIData = async (url) => {
  let returnData = null;
  const settings = {
    url: url,
    method: "GET",
  };
  await $.ajax(settings)
    .done((data) => {
      // console.log(data);
      if (data.success == true) {
        returnData = data.data;
      }
      Loading(false);
    })
    .fail((xhr, status, error) => {
      Loading(false);
      console.log(xhr.responseText);
    });
  return returnData;
};

/**
 * create dropdown jquery
 *
 * @param {List(obj)} data - list object
 * @param {string} name - name attr select
 * @returns
 */
const createDropdown = (data, name, selectedId = null) => {
  const select = $("<select>").addClass("form-select " + name);
  select.css({
    width: "100%",
  });
  select.prop("required", true);
  select.prop("name", name);
  $.each(data, (index, value) => {
    const option = $("<option>");
    option.val(value.id);
    if (name == "org") {
      option.text(
        (value.levelNameEN ? "(" + value.levelNameEN + ") " : "") +
          value.nameEN +
          (value.shortName ? " (" + value.shortName + ")" : "")
      );
    } else {
      option.text(
        (value.code ? "(" + value.code + ") " : "") +
          value.nameEN +
          (value.shortName ? " (" + value.shortName + ")" : "")
      );
    }
    if (selectedId == value.id) {
      option.prop("selected", true);
    }
    select.append(option);
  });
  return select;
};

const createTableRole = (pos, orgs, seletedPos = null, seletedOrg = null) => {
  const posSelect = createDropdown(pos, "pos", seletedPos);
  const orgSelect = createDropdown(orgs, "org", seletedOrg);
  // -- div invalid feed back
  const invalidDiv = $("<div>").addClass("invalid-feedback");
  invalidDiv.text("Please select Data");
  const button = $("<button>", {
    type: "button",
    text: "Delete",
    class: "btn btn-danger delete",
  });
  // -- <td>
  const td = $("<td>");

  // -- td organization column
  const tdOrg = td.clone().append(orgSelect);
  tdOrg.append(invalidDiv.clone());
  // -- td position column
  const tdPos = td.clone().append(posSelect);
  tdPos.append(invalidDiv.clone());
  // -- td delete button column
  const tdDl = td.clone().append(button);
  // -- <tr>
  const tr = $("<tr>");
  tr.append(tdOrg);
  tr.append(tdPos);
  tr.append(tdDl);
  if (!$(".table > tbody")[0]) {
    const tbody = $("<tbody>");
    tbody.append(tr);
    const table = $(".table");
    table.append(tbody);
  } else {
    const table = $(".table > tbody");
    table.append(tr);
  }
};

function strUTCDateToStrThaiDate(dateString) {
  const date = new Date(dateString);
  const result = date.toLocaleString("th-TH", {
    timeZone: "Asia/Bangkok",
    year: "numeric",
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  return result;
}

// -- car schedule : create passenger table -- //

class PassengerTable {
  constructor(headers = []) {
    this.headers = headers;
    this.rows = []; // { data: [...], val: ... }
    this.$table = null;
    this.$tbody = null;
  }

  addRow(data) {
    this.rows.push(data);
    if (this.$tbody) {
      this.refresh();
    }
  }

  removeRow(index) {
    let removed = this.rows[index];
    this.rows.splice(index, 1);
    this.refresh();

    // enable dropdown option กลับคืน
    if (removed && removed.val) {
      $("#passenger option[value='" + removed.val + "']").prop(
        "disabled",
        false
      );
    }

    // ถ้า row หมด → clear table ออกไป
    if (this.rows.length === 0) {
      this.clear();
    }
  }

  clear() {
    if (this.$table) {
      this.$table.remove(); // ลบ DOM ออก
    }
    this.$table = null;
    this.$tbody = null;
    this.rows = []; // reset array ด้วย
  }

  render() {
    this.$table = $("<table>").addClass(
      "align-middle table table-bordered table-hover table-primary table-striped"
    );

    if (this.headers.length > 0) {
      let $thead = $("<thead>");
      let $tr = $("<tr>");
      this.headers.forEach((h) => $tr.append($("<th>").html(h)));
      $thead.append($tr);
      this.$table.append($thead);
    }

    this.$tbody = $("<tbody>");
    this.$table.append(this.$tbody);

    this.refresh();
    return this.$table;
  }

  refresh() {
    if (!this.$tbody) return;
    this.$tbody.empty();

    this.rows.forEach((row, idx) => {
      let $tr = $("<tr>").attr("data-value", row.val);
      let $inputHiddenId = $("<input>", {
        type: "hidden",
        name: "psgs[]",
        value: row.val,
      });

      row.data.forEach((cell) => {
        $tr.append($("<td>").html(cell));
      });

      let $actionTd = $("<td>");
      let $btnDel = $("<button>", {
        class: "btn btn-sm btn-danger",
        text: "Remove",
      }).on("click", () => this.removeRow(idx));

      $actionTd.append($btnDel);
      $actionTd.append($inputHiddenId);
      $tr.append($actionTd);
      this.$tbody.append($tr);
    });
  }
}
