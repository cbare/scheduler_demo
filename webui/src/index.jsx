import React from 'react';
import ReactDOM from 'react-dom';
import 'whatwg-fetch';
import moment from 'moment';



class SelectCoach extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      value: 1,
      coaches: []
    };
    this.handleChange = this.handleChange.bind(this);
  }

  componentDidMount() {
    fetch("http://127.0.0.1:5000/coaches/").then(
      (response) => {
        response.json().then((coaches) => {
          this.setState({
            coaches:coaches, 
            value:coaches.length>0 ? coaches[0].id : 0})
        })
      },
      (error) => {
        console.log("Error: "+error.message)
      }
    )
  }
  handleChange(event) {
    console.log("handleChange", event.target.value)
    this.setState({value: event.target.value});
    this.props.handleCoachChange(event.target.value);
  }

  render() {
    const options = this.state.coaches.map((coach) =>
      <option key={coach.id} value={coach.id}>{coach.first_name} {coach.last_name}</option>)
    return (
      <form>
        <label>
          Select a coach:&nbsp;
          <select value={this.state.value} onChange={this.handleChange}>
            {options}
          </select>
        </label>
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
  return (
    <button className={props.type=="open slot" ? "square open" : "square unavailable"}
      onClick={()=>props.onClick(props.start_time, props.end_time)}
      style={{position:'absolute', top:props.top, height:props.height}}>
      {props.description}
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
                    description={ap.name}
                    onClick={this.foo} 
                    start_time={ap.start_time}
                    end_time={ap.end_time}
                    type={ap.type}
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

class WeekCalendar extends React.Component {
  constructor() {
    super();
    console.log("today=", moment().format())
    var calendarDate = moment().startOf('week')
    console.log("startOf week =", calendarDate.format())
    if (moment().day() > 4 ) {
      calendarDate.add(1, 'week')
    }
    this.state = {
      coach_name: '',
      coach_id: 1,
      calendarDate: calendarDate,
      events: []
    };
  }
  fetchAppointments(coach_id, from, to) {
    const url = "http://127.0.0.1:5000/schedule/"+coach_id+
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
  handleCoachChange(coach_id) {
    console.log('handleCoachChange to ', coach_id)
    this.setState({coach_id: coach_id});
    this.fetchAppointments(coach_id, this.state.calendarDate, moment(this.state.calendarDate).add(1,'week'))
  }
  moveLeft() {
    this.setState({calendarDate:this.state.calendarDate.subtract(1,'week')})
    console.log(this.state.calendarDate.format())
    this.fetchAppointments(this.state.coach_id, this.state.calendarDate, moment(this.state.calendarDate).add(1,'week'))
  }
  moveRight() {
    this.setState({calendarDate:this.state.calendarDate.add(1,'week')})
    console.log(this.state.calendarDate.format())
    this.fetchAppointments(this.state.coach_id, this.state.calendarDate, moment(this.state.calendarDate).add(1,'week'))
  }
  componentDidMount() {
    this.fetchAppointments(this.state.coach_id, this.state.calendarDate, moment(this.state.calendarDate).add(1,'week'))
  }
  render() {
    return (
      <div>
        <SelectCoach handleCoachChange={(component)=>this.handleCoachChange(component)}/>
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
                        events={this.state.events}/>
          </tbody>
        </table>
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
