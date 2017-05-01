/**
 * This file provides inputs for the user to do a text search.
 *
 * Author: Team EndFrame
 * Organization: Bucknell University
 * Spring 2017
 */

import * as React from 'react';
import FlatButton from 'material-ui/FlatButton';
import SelectField from 'material-ui/SelectField';
import MenuItem from 'material-ui/MenuItem';
import TextField from 'material-ui/TextField';
import {connect} from 'react-redux';
import {hashHistory} from 'react-router';
import Dialog from 'material-ui/Dialog';
import {STOP_WORDS, GENRES} from '../helpers';

const modalStyle = {
    textAlign: 'center'
};

const inputStyle = {
    top: '20px',
    float: 'left',
    width: '35%',
    marginLeft: '5%'
};

const sortStyle = {
    top: '-4px',
    width: '20%',
    float: 'left'
};

const buttonStyle = {
    top: '27px',
    float: 'left'
}

const SearchIcon = (props) => {
    return (
        <svg {...props} fill="#000000" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            <path d="M0 0h24v24H0z" fill="none"/>
        </svg>
    );
};


/**
 * Uses Material-UI input components and dropdowns to allow user input for a text based search.
 */
@connect(mapStateToProps, mapDispatchToProps)
export default class TextInputModal extends React.Component {


    constructor() {
        super();

        this.state = {
            open: false,
            searchText: '',
            errorText: ''
        };

        this.handleOpen = this.handleOpen.bind(this);
        this.handleClose = this.handleClose.bind(this);
        this.updateSearchForEnterKeypress = this.updateSearchForEnterKeypress.bind(this);
        this.handleChange = this.handleChange.bind(this);
    }

    static cleanStopWords(input) {
        let splitString = input.toLowerCase().split(' ');
        var buildString = '';
        for (var i = 0; i < splitString.length; i++) {
            if (!(STOP_WORDS.includes(splitString[i]))) {
                // If it is the first non stop word
                if (buildString == '') {
                    buildString = splitString[i];
                }
                // If it is a middle non stop word or last non stop word
                else {
                    buildString = buildString + ' ' + splitString[i];
                }
            }
        }
        return buildString;
    }


    updateSearch() {
        // stop default form submission behavior
        event.preventDefault();

        let keywordOrPhrase = this.refs["updateSearchBox"].getValue();
        keywordOrPhrase = TextInputModal.cleanStopWords(keywordOrPhrase);

        this.setState({searchText: ''});

        // update the URL
        let newPath = `/${keywordOrPhrase.replace(/ /g, '&').replace('!','').replace('?','')}`;
        hashHistory.push(newPath);
        if (keywordOrPhrase === '') {
            this.state.errorText = 'Your search has returned too many results.';
        }
        else {
            this.state.errorText = '';
        }
    }

    handleOpen() {
        this.setState({open: true});
    };

    handleClose() {
        this.setState({open: false});
    };

    updateSearchForEnterKeypress(event) {

        // stop default form submission behavior
        event.preventDefault();

        this.updateSearch();
    }

    handleChange(event, newValue) {
        this.setState({searchText: newValue});
    }


    render() {

        return (
                <div id="textIconImage">
                    <img src="/static/imageFiles/textIcon.jpg" onTouchTap={this.handleOpen}></img>
                    <Dialog
                        style={modalStyle}
                        modal={false}
                        open={this.state.open}
                        autoScrollBodyContent={true}
                        onRequestClose={this.handleClose}
                    >
                        <form id='textForm' onSubmit={this.updateSearchForEnterKeypress}>
                            <TextField
                                hintText="Search Phrase"
                                errorText={this.state.errorText}
                                value={this.state.searchText}
                                style={inputStyle}
                                onChange={this.handleChange}
                                ref="updateSearchBox"
                            />
                        </form>

                        <SelectField
                            floatingLabelText="Sort"
                            value={this.props.sortType}
                            onChange={this.props.onSelectSortType}
                            style={sortStyle}
                        >
                            <MenuItem value={1} primaryText="Relevance" />
                            <MenuItem value={2} primaryText="Movie Title (A-Z)" />
                            <MenuItem value={3} primaryText="Movie Title (Z-A)" />
                            <MenuItem value={4} primaryText="Year (New to Old)" />
                            <MenuItem value={5} primaryText="Year (Old to New)" />
                        </SelectField>

                        <SelectField
                            floatingLabelText="Genre"
                            value={this.props.genre}
                            onChange={this.props.onSelectGenre}
                            style={sortStyle}
                            maxHeight={200}
                        >
                            {GENRES.map((genre, index) => <MenuItem key={genre} value={genre} primaryText={genre} />) }
                        </SelectField>
                        <FlatButton
                            label="Search"
                            labelPosition="before"
                            primary={true}
                            icon={<SearchIcon style={{verticalAlign: 'middle'}}/>}
                            onClick={() => this.updateSearch()}
                            style={buttonStyle}
                        />

                    </Dialog>
                </div>
        );
    }
}


const selectSortType = (sortType) => {
    return {
        type: "SELECT_SORT_TYPE",
        sortType
    }
};

const selectGenre = (genre) => {
    return {
        type: "SELECT_GENRE",
        genre
    }
};

// Map Redux state to component props
function mapStateToProps(state) {
    return {
        sortType: state.sortType,
        genre: state.genre,
        enableSort: state.search != null && state.search.searchType == "text",
        currentOclcId: state.currentMovieOclcId,
        searchTerm: state.search != null && state.search.searchTerm ? state.search.searchTerm : ''
    }
}

// Map Redux actions to component props
function mapDispatchToProps(dispatch) {
    return {
        onSelectSortType: (event, index, sortType) => dispatch(selectSortType(sortType)),
        onSelectGenre: (event, index, genre) => dispatch(selectGenre(genre))
    }
}
