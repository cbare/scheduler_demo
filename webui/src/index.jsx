import React from 'react';
import ReactDOM from 'react-dom';
import 'whatwg-fetch';
import moment from 'moment';

import Button from 'react-bootstrap/lib/Button';
import Modal from 'react-bootstrap/lib/Modal';
import Popover from 'react-bootstrap/lib/Popover';
import Tooltip from 'react-bootstrap/lib/Tooltip';
import OverlayTrigger from 'react-bootstrap/lib/OverlayTrigger';

function formatName(person) {
  return person ? person.first_name + ' ' + person.last_name : ''
}

function checkStatus(response) {
  if (response.status >= 200 && response.status < 300) {
    return response
  } else {
    var error = new Error(response.statusText)
    error.response = response
    throw error
  }
}


class SelectCoach extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      value: 0,
      coaches_by_id: new Map()
    };
    this.handleChange = this.handleChange.bind(this)
  }

  componentDidMount() {
    fetch("http://127.0.0.1:5000/coaches/").then(
      (response) => {
        response.json().then((coaches) => {
          this.setState({
            coaches_by_id: new Map(coaches.map((coach)=>[coach.id, coach])),
            value:0})
        })
      },
      (error) => {
        console.log("Error: "+error.message)
      }
    )
  }

  handleChange(event) {
    this.setState({value: event.target.value});
    this.props.selectCoach(this.state.coaches_by_id.get(1*event.target.value));
  }

  render() {
    const options = Array.from(this.state.coaches_by_id.values()).map((coach) =>
      <option key={coach.id} value={coach.id}>{coach.first_name} {coach.last_name}</option>)
    if (this.state.value==0) {
      options.unshift(<option key={0} value={0}>Select a coach</option>)
    }
    return (
      <form>
        <label>
          Coach:&nbsp;
        </label>
        <select value={this.state.value} onChange={this.handleChange}>
          {options}
        </select>
      </form>
    );
  }
}

function LeftButton(props) {
  return(
    <th className="back" onClick={() => props.onClick()}>&lt;</th>
  )
}

function RightButton(props) {
  return(
    <th className="forward" onClick={() => props.onClick()}>&gt;</th>
  )
}

function MonthLabel(props) {
  var last = moment(props.calendarDate).add(6,'days');
  var monthLabel = props.calendarDate.month()==last.month() ?
          props.calendarDate.format("MMMM") :
          props.calendarDate.format("MMMM") + "/" + last.format("MMMM");
  return(
    <tr className="board-row">
      <LeftButton onClick={props.onLeftButtonClick}/>
      <th className="month-label">{monthLabel}</th>
      <RightButton onClick={props.onRightButtonClick}/>
    </tr>
  )
}

function DayLabels(props) {
  const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((d,i) =>
    <td className="day-label" key={d}>{d} {moment(props.calendarDate).add(i,'day').date()}</td>
  );
  return(
    <tr className="board-row">
      {dayLabels}
    </tr>
  )
}

function Square(props) {
  return (
    <button className="square" onClick={() => props.onClick()}>
      {props.value}
    </button>
  );
}

function AppointmentSlot(props) {
  const ap = props.appointment
  const label = ap.start_time.format('hh:mm a')
  return (
    <button className={ap.type=="open slot" ? "square open" : "square unavailable"}
      onClick={()=>props.onClick(props)}
      style={{position:'absolute', top:props.top, height:props.height}}>
      {label}
    </button>
  );
}

class DayColumns extends React.Component {
  render() {
    const dayColumns = [0,1,2,3,4,5,6].map((wd) => {
      const startOfDay = moment(this.props.calendarDate).add(wd, 'days').add(8,'hours')
      const endOfDay = moment(startOfDay).add(10,'hours')
      const appointments = this.props.events.
              filter((ap) => ap.start_time < endOfDay && ap.end_time >= startOfDay).
              map((ap) => {
                const top = ap.start_time.diff(startOfDay, 'minutes') * 500/600;
                const height = ap.end_time.diff(ap.start_time, 'minutes') * 500/600-2;
                return (
                  <AppointmentSlot
                    key={ap.key}
                    appointment={ap}
                    onClick={this.props.appointmentDialogOpen}
                    top={top}
                    height={height} />
                )
              })
      return (
        <td key={wd} className="day-column">
          <div className="day-column-div">
            {appointments}
          </div>
        </td>
      )
    })
    return(
      <tr className="day-columns-row">
        {dayColumns}
      </tr>
    )
  }
}


class ScheduleDialog extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      showModal: false,
      description: "Coaching session"
    }
    this.handleDescriptionChange = this.handleDescriptionChange.bind(this)
  }
  componentWillReceiveProps(nextProps) {
    this.setState({ showModal:nextProps.is_visible })
  }
  close() {
    //this.setState({ showModal: false });
    this.props.appointmentDialogClose()
  }
  open() {
    this.setState({ showModal: true });
  }
  handleDescriptionChange(event) {
    this.setState({description: event.target.value});
  }
  render() {
    const start_time = this.props.appointment ? this.props.appointment.start_time.format('h:mm a') : null
    const end_time = this.props.appointment ? this.props.appointment.end_time.format('h:mm a') : null
    const date = this.props.appointment ? this.props.appointment.start_time.format('LL') : null
    return (
      <Modal show={this.state.showModal} onHide={() => this.close()}>
        <Modal.Header closeButton>
          <Modal.Title>Book a Coaching Session</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <h4>Schedule an appointment with <span>{formatName(this.props.coach)}</span></h4>
          <table>
            <tbody>
              <tr>
                <th>Date</th>
                <td>{date}</td>
              </tr>
              <tr>
                <th>Start time</th>
                <td>{start_time}</td>
              </tr>
              <tr>
                <th>End time</th>
                <td>{end_time}</td>
              </tr>
              <tr>
                <th>Coach</th>
                <td>{formatName(this.props.coach)}</td>
              </tr>
              <tr>
                <th>Client</th>
                <td>{formatName(this.props.client)}</td>
              </tr>
              <tr>
                <th>Description</th>
                <td><textarea value={this.state.description} onChange={this.handleDescriptionChange} /></td>
              </tr>
            </tbody>
          </table>
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={() => this.props.scheduleAppointment(this.state.description)}>Book It!</Button>
          <Button onClick={() => this.close()}>Cancel</Button>
        </Modal.Footer>
      </Modal>
    )
  }
}


class WeekCalendar extends React.Component {
  constructor() {
    super()
    console.log("today=", moment().format())
    var calendarDate = moment().startOf('week')
    console.log("startOf week =", calendarDate.format())
    if (moment().day() > 4 ) {
      calendarDate.add(1, 'week')
    }
    // TODO: replace hard-coded user with authenticated user
    this.state = {
      user: {id:12, first_name:'Virgil', last_name:'Venable'},
      selected_coach: null,
      appointment: null,
      calendarDate: calendarDate,
      events: [],
      showAppointmentDialog:false,
      status: null
    };
    this.appointmentDialogClose = this.appointmentDialogClose.bind(this)
    this.appointmentDialogClose = this.appointmentDialogClose.bind(this)
    this.scheduleAppointment    = this.scheduleAppointment.bind(this)
  }
  componentDidMount() {
    this.fetchAppointments(this.state.selected_coach, this.state.calendarDate, moment(this.state.calendarDate).add(1,'week'))
  }
  fetchAppointments(coach, from, to) {
    if (coach) {
      const url = "http://127.0.0.1:5000/schedule/"+coach.id+
                  "/?from=" + from.toISOString() + "&to=" + to.toISOString()
      console.log(url)
      fetch(url).then(
        (response) => {
          response.json().then((events) => {
            if (events && events.length) {
              console.log('fetched ' + events.length + ' appointment slots.')
            }
            else {
              console.log('received no appointment slots.')
            }
            for (var i=0; i<events.length; i++) {
              events[i].key = i
              events[i].start_time = moment(events[i].start_time).local()
              events[i].end_time = moment(events[i].end_time).local()
            }
            this.setState({events:events})
          })
        },
        (error) => {
          console.log("Error: "+error.message)
        }
      )
    }
  }
  appointmentDialogOpen(props) {
    console.log("scheduleAppointmentDialogOpen: ", props)
    this.setState({appointment:props.appointment, showAppointmentDialog:true})
  }
  appointmentDialogClose() {
    this.setState({showAppointmentDialog:false}) 
  }
  scheduleAppointment(description) {
    const ap = this.state.appointment
    const ap_request = {
      start_time:ap.start_time,
      end_time:ap.end_time,
      name:'Coaching session',
      type:'coaching',
      notes:description,
      participants:[this.state.selected_coach.id,
                    this.state.user.id]
    }
    fetch("http://127.0.0.1:5000/event/", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(ap_request)
      })
        .then(checkStatus)
        .then((response)=>response.json())
        .then((json) => {
            //this.setState({status:status.status})
            console.log('created booking', json)
          })
        .catch((error) => {
            console.log("Error: "+error.message)
          })
    this.appointmentDialogClose()
  }
  selectCoach(coach) {
    console.log('selectCoach to ', coach.id, coach.first_name, coach.last_name)
    this.setState({selected_coach: coach});
    this.fetchAppointments(coach, this.state.calendarDate, moment(this.state.calendarDate).add(1,'week'))
  }
  moveLeft() {
    this.setState({calendarDate:this.state.calendarDate.subtract(1,'week')})
    console.log(this.state.calendarDate.format())
    this.fetchAppointments(this.state.selected_coach, this.state.calendarDate, moment(this.state.calendarDate).add(1,'week'))
  }
  moveRight() {
    this.setState({calendarDate:this.state.calendarDate.add(1,'week')})
    console.log(this.state.calendarDate.format())
    this.fetchAppointments(this.state.selected_coach, this.state.calendarDate, moment(this.state.calendarDate).add(1,'week'))
  }
  render() {
    return (
      <div>
        <SelectCoach selectCoach={(component)=>this.selectCoach(component)}/>
        <table className="calendar">
          <thead>
            <MonthLabel 
              onLeftButtonClick={() => this.moveLeft()}
              onRightButtonClick={() => this.moveRight()}
              calendarDate={this.state.calendarDate}/>
            <DayLabels calendarDate={this.state.calendarDate}/>
          </thead>
          <tbody>
            <DayColumns calendarDate={this.state.calendarDate}
                        events={this.state.events}
                        appointmentDialogOpen={(props) => this.appointmentDialogOpen(props)}/>
          </tbody>
        </table>
        <ScheduleDialog
          appointment={this.state.appointment}
          coach={this.state.selected_coach}
          client={this.state.user}
          ref={(scheduleDialog) => { this.scheduleDialog = scheduleDialog }}
          is_visible={this.state.showAppointmentDialog}
          appointmentDialogClose={this.appointmentDialogClose}
          scheduleAppointment={this.scheduleAppointment}
          />
      </div>
    )
  }
}

ReactDOM.render(
  <div>
  <h1>Schedule a coaching session</h1>
  <WeekCalendar />
  </div>,
  document.getElementById('app')
);
