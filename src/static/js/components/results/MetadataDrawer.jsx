import * as React from "react";
import Drawer from 'material-ui/Drawer';
import {connect} from 'react-redux';
import Roboto from 'material-ui/FontIcon';
import Paper from 'material-ui/Paper'

import {DEBUG_MODE} from "../../app.jsx";

import LazyLoad from 'react-lazyload';
import CircularProgress from 'material-ui/CircularProgress';
import {black} from "material-ui/styles/colors";

import {createSelector} from 'reselect';

const timeLineLength = 200;

@connect(mapStateToProps)
export default class MetadataDrawer extends React.Component {

    static timeStampToMinutes(movieStartTimeStamp, totalMovieRuntime) {
        const splitString = movieStartTimeStamp.split(":");
        return Math.ceil((10 + parseInt(splitString[0]) * 60 + parseInt(splitString[1]))/totalMovieRuntime*timeLineLength);
    }

    /* Removes the junk after the comma in the screenshot's timestamp */
    static beautifyTimeStamp(movieStartTimeStamp) {
        const splitString = movieStartTimeStamp.split(",");
        return (splitString[0]);
    }

    render() {

        // if there's no film to show in the metadata (because the user hasn't scrolled down yet), show the first film
        let movieDetails = this.props.movieDetails;

        let imgSrc = movieDetails != null ? "http://www.filmtvsearch.net/static/imageFiles/" + movieDetails.movieOclcId + ".gif" : null;
        
        return (
            <Drawer docked={true} open={true} openSecondary={true} zDepth={2} containerStyle={{height: 'calc(100% - 56px)', top: 56}}>
                {movieDetails == null ? (
                        <div>Mouse over a film for details ;) <br /></div>
                    ) : (
                        <div>
                            <div className="movieTitleInMetadataDrawer">
                                {movieDetails.movieTitle} ({movieDetails.movieReleaseYear}) <br />
                            </div>
                                <LazyLoad height={197} placeholder={<CircularProgress />}>
                                    <img className="thumbnail" src={imgSrc} width="140" height="197" />
                                </LazyLoad>
                        </div>
                    )
                }

                {this.props.screenshotDetails != null ? (
                    <div>
                        <div className="metadataDrawerDialogueContainer">
                            {movieDetails.runtimeInMinutes} minutes <br /> <br />
                            Line {this.props.screenshotDetails.movieLineNumber}: <br />
                            "{this.props.screenshotDetails.movieLineText}" <br />
                        </div>

                        <Paper>
                        <div className="metadataDrawerTimelineContainer">
                            <svg height="70" width="200">
                                <line x1="10" y1="50" x2="210" y2="50" stroke={"grey"} strokeWidth={1} />
                                <line x1={MetadataDrawer.timeStampToMinutes(this.props.screenshotDetails.movieStartTimeStamp, this.props.movieDetails.runtimeInMinutes)} y1="30" x2={MetadataDrawer.timeStampToMinutes(this.props.screenshotDetails.movieStartTimeStamp, this.props.movieDetails.runtimeInMinutes)} y2="65" stroke={"gray"} strokeWidth={1}/>
                            </svg>
                            {MetadataDrawer.beautifyTimeStamp(this.props.screenshotDetails.movieStartTimeStamp)}
                        </div>
                        </Paper>
                    </div>
                    ): null
                }
            </Drawer>
        )
    }
}

const getHoverMovieOclcId = (state) => state.hoverMovieOclcId;

const getHoverMovieLineNumber = (state) => state.hoverMovieLineNumber;

const getCurrentMovieOclcId = (state) => state.currentMovieOclcId;

const getSearchResponse = (state) => state.search && state.search.response;

const getMovieDetails = createSelector(
    [getHoverMovieOclcId, getCurrentMovieOclcId, getSearchResponse],
    (hoverMovieOclcId, currentMovieOclcId, searchResponse) => {
        // screenshot is being hovered
        if (hoverMovieOclcId) {
            return {...searchResponse.find((x) => x.movieOclcId == hoverMovieOclcId)};
        }
        else {
            return null;
        }
    }
);

const getScreenshotDetails = createSelector(
    [getHoverMovieLineNumber, getMovieDetails],
    (hoverMovieLineNumber, movieDetails) => {
        if (hoverMovieLineNumber) {
            return movieDetails.results.find((x) => x.movieLineNumber == hoverMovieLineNumber);
        }
        else {
            return null;
        }
    }
);

// Map Redux state to component props
function mapStateToProps(state) {
    return {
        movieDetails: getMovieDetails(state),
        screenshotDetails: getScreenshotDetails(state)
    }
}
